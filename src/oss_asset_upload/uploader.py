"""OSS upload implementation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alibabacloud_oss_v2.client import Client

from .config import OssConfig
from .media import guess_content_type, media_kind
from .naming import file_sha256, object_key_for_file


@dataclass(frozen=True)
class UploadedAsset:
    local_path: str
    object_key: str
    url: str
    content_type: str
    kind: str
    size: int
    sha256: str
    etag: str | None = None
    dry_run: bool = False

    def to_dict(self) -> dict[str, object | None]:
        return asdict(self)


class OssAssetUploader:
    def __init__(self, config: OssConfig) -> None:
        self.config = config
        self._client: "Client | None" = None

    @property
    def client(self) -> "Client":
        if self._client is None:
            from alibabacloud_oss_v2 import config as oss_config
            from alibabacloud_oss_v2.client import Client
            from alibabacloud_oss_v2.credentials.provider_impl import StaticCredentialsProvider

            credentials_provider = StaticCredentialsProvider(
                self.config.access_key_id,
                self.config.access_key_secret,
                self.config.security_token,
            )
            cfg = oss_config.Config(
                region=self.config.region,
                endpoint=self.config.sdk_endpoint,
                credentials_provider=credentials_provider,
                connect_timeout=30,
                readwrite_timeout=120,
            )
            self._client = Client(cfg)
        return self._client

    def prepare_asset(self, path: str | Path, *, prefix: str, include_hash: bool = True) -> UploadedAsset:
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {source}")

        digest = file_sha256(source)
        object_key = object_key_for_file(source, prefix=prefix, digest=digest, include_hash=include_hash)
        content_type = guess_content_type(source)
        return UploadedAsset(
            local_path=str(source),
            object_key=object_key,
            url=self.config.public_url(object_key),
            content_type=content_type,
            kind=media_kind(content_type),
            size=source.stat().st_size,
            sha256=digest,
        )

    def upload_asset(
        self,
        asset: UploadedAsset,
        *,
        cache_control: str | None = None,
        forbid_overwrite: bool = False,
        dry_run: bool = False,
    ) -> UploadedAsset:
        if dry_run:
            return UploadedAsset(**{**asset.to_dict(), "dry_run": True})

        source = Path(asset.local_path)
        with source.open("rb") as body:
            from alibabacloud_oss_v2 import models as oss_models

            request = oss_models.PutObjectRequest(
                bucket=self.config.bucket,
                key=asset.object_key,
                body=body,
                content_length=asset.size,
                content_type=asset.content_type,
                cache_control=cache_control or self.config.cache_control,
                forbid_overwrite=forbid_overwrite,
            )
            result = self.client.put_object(request)

        etag = getattr(result, "etag", None)
        return UploadedAsset(**{**asset.to_dict(), "etag": etag, "dry_run": False})
