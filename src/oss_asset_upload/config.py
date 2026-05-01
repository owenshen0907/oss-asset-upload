"""Configuration loading for OSS asset uploads."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required OSS configuration is missing or invalid."""


@dataclass(frozen=True)
class OssConfig:
    access_key_id: str
    access_key_secret: str
    endpoint: str
    region: str
    bucket: str
    security_token: str | None = None
    public_base_url: str | None = None
    asset_prefix: str = "notes"
    cache_control: str = "public, max-age=31536000, immutable"

    @property
    def sdk_endpoint(self) -> str:
        return normalize_endpoint(self.endpoint)

    def public_url(self, object_key: str) -> str:
        key = quote_object_key(object_key)
        if self.public_base_url:
            return f"{self.public_base_url.rstrip('/')}/{key}"

        parsed = urlparse(self.sdk_endpoint)
        return f"{parsed.scheme}://{self.bucket}.{parsed.netloc}/{key}"


def normalize_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if endpoint.startswith(("http://", "https://")):
        return endpoint.rstrip("/")
    return f"https://{endpoint.rstrip('/')}"


def quote_object_key(object_key: str) -> str:
    from urllib.parse import quote

    return quote(object_key.lstrip("/"), safe="/")


def _get(name: str, overrides: dict[str, str | None]) -> str | None:
    value = overrides.get(name)
    if value is not None:
        return value
    return os.getenv(name)


def load_config(
    *,
    env_file: str | Path | None = None,
    bucket: str | None = None,
    endpoint: str | None = None,
    region: str | None = None,
    public_base_url: str | None = None,
    prefix: str | None = None,
) -> OssConfig:
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    overrides = {
        "OSS_BUCKET": bucket,
        "OSS_ENDPOINT": endpoint,
        "OSS_REGION": region,
        "OSS_PUBLIC_BASE_URL": public_base_url,
        "OSS_ASSET_PREFIX": prefix,
    }

    access_key_id = _get("OSS_ACCESS_KEY_ID", overrides)
    access_key_secret = _get("OSS_ACCESS_KEY_SECRET", overrides)
    resolved_endpoint = _get("OSS_ENDPOINT", overrides)
    resolved_bucket = _get("OSS_BUCKET", overrides)
    resolved_region = _get("OSS_REGION", overrides) or "cn-shanghai"
    resolved_prefix = _get("OSS_ASSET_PREFIX", overrides) or "notes"
    resolved_public_base_url = _get("OSS_PUBLIC_BASE_URL", overrides) or None
    cache_control = os.getenv("OSS_CACHE_CONTROL") or "public, max-age=31536000, immutable"

    required = {
        "OSS_ACCESS_KEY_ID": access_key_id,
        "OSS_ACCESS_KEY_SECRET": access_key_secret,
        "OSS_ENDPOINT": resolved_endpoint,
        "OSS_BUCKET": resolved_bucket,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ConfigError("Missing required environment variables: " + ", ".join(missing))

    return OssConfig(
        access_key_id=access_key_id or "",
        access_key_secret=access_key_secret or "",
        endpoint=resolved_endpoint or "",
        region=resolved_region,
        bucket=resolved_bucket or "",
        security_token=os.getenv("OSS_SECURITY_TOKEN") or None,
        public_base_url=resolved_public_base_url,
        asset_prefix=resolved_prefix.strip("/"),
        cache_control=cache_control,
    )
