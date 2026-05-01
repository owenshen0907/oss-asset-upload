"""Render uploaded assets for Markdown documents."""

from __future__ import annotations

import json
from pathlib import Path

from .uploader import UploadedAsset


def default_label(asset: UploadedAsset) -> str:
    return Path(asset.local_path).stem.replace("-", " ").replace("_", " ").strip() or "asset"


def render_one(asset: UploadedAsset, *, output: str = "markdown", caption: str | None = None) -> str:
    label = caption or default_label(asset)
    if output == "json":
        return json.dumps(asset.to_dict(), ensure_ascii=False, indent=2)
    if output == "url":
        return asset.url
    if output == "html":
        return render_html(asset, label)
    if output == "markdown":
        return render_markdown(asset, label)
    raise ValueError(f"Unsupported output format: {output}")


def render_many(assets: list[UploadedAsset], *, output: str = "markdown", caption: str | None = None) -> str:
    if output == "json":
        return json.dumps([asset.to_dict() for asset in assets], ensure_ascii=False, indent=2)
    return "\n\n".join(render_one(asset, output=output, caption=caption) for asset in assets)


def render_markdown(asset: UploadedAsset, label: str) -> str:
    if asset.kind == "image":
        return f"![{label}]({asset.url})"
    if asset.kind in {"audio", "video"}:
        return render_html(asset, label)
    return f"[{label}]({asset.url})"


def render_html(asset: UploadedAsset, label: str) -> str:
    if asset.kind == "image":
        return (
            "<figure>\n"
            f'  <img src="{asset.url}" alt="{label}" />\n'
            f"  <figcaption>{label}</figcaption>\n"
            "</figure>"
        )
    if asset.kind == "audio":
        return (
            "<figure>\n"
            f'  <audio controls src="{asset.url}"></audio>\n'
            f"  <figcaption>{label}</figcaption>\n"
            "</figure>"
        )
    if asset.kind == "video":
        return (
            "<figure>\n"
            f'  <video controls playsinline src="{asset.url}"></video>\n'
            f"  <figcaption>{label}</figcaption>\n"
            "</figure>"
        )
    return f'<a href="{asset.url}">{label}</a>'
