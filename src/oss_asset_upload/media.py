"""Media type helpers."""

from __future__ import annotations

import mimetypes
from pathlib import Path


_KIND_BY_PREFIX = {
    "image/": "image",
    "audio/": "audio",
    "video/": "video",
}


def guess_content_type(path: str | Path) -> str:
    content_type, _ = mimetypes.guess_type(str(path))
    return content_type or "application/octet-stream"


def media_kind(content_type: str) -> str:
    for prefix, kind in _KIND_BY_PREFIX.items():
        if content_type.startswith(prefix):
            return kind
    return "file"
