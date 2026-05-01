"""Object key naming helpers."""

from __future__ import annotations

from datetime import date, datetime
import hashlib
from pathlib import Path
import re
import unicodedata

_SAFE_CHARS = re.compile(r"[^a-z0-9._-]+")
_DASHES = re.compile(r"-+")


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str, *, fallback: str = "asset") -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower().strip()
    lowered = _SAFE_CHARS.sub("-", lowered)
    lowered = _DASHES.sub("-", lowered).strip("-._")
    return lowered or fallback


def normalize_prefix(prefix: str) -> str:
    parts = [slugify(part, fallback="asset") for part in prefix.replace("\\", "/").split("/")]
    return "/".join(part for part in parts if part)


def parse_asset_date(value: str | None) -> date:
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def dated_slug_prefix(base_prefix: str, slug: str | None, value: str | None) -> str:
    base = normalize_prefix(base_prefix or "notes")
    if not slug:
        return base
    asset_date = parse_asset_date(value)
    return normalize_prefix(f"{base}/{asset_date:%Y}/{asset_date:%m}/{slug}")


def object_name_for_file(path: str | Path, *, digest: str | None = None, include_hash: bool = True) -> str:
    source = Path(path)
    stem = slugify(source.stem)
    suffix = source.suffix.lower()
    if include_hash:
        digest = digest or file_sha256(source)
        return f"{stem}-{digest[:8]}{suffix}"
    return f"{stem}{suffix}"


def object_key_for_file(
    path: str | Path,
    *,
    prefix: str,
    digest: str | None = None,
    include_hash: bool = True,
) -> str:
    clean_prefix = normalize_prefix(prefix)
    object_name = object_name_for_file(path, digest=digest, include_hash=include_hash)
    return f"{clean_prefix}/{object_name}" if clean_prefix else object_name
