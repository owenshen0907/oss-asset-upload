from oss_asset_upload.render import render_one
from oss_asset_upload.uploader import UploadedAsset


def asset(kind: str, content_type: str, url: str):
    return UploadedAsset(
        local_path="/tmp/demo-file.png",
        object_key="notes/demo-file.png",
        url=url,
        content_type=content_type,
        kind=kind,
        size=10,
        sha256="abc",
    )


def test_render_image_markdown():
    rendered = render_one(asset("image", "image/png", "https://cdn.example.com/a.png"), output="markdown")
    assert rendered == "![demo file](https://cdn.example.com/a.png)"


def test_render_audio_markdown_uses_html_figure():
    rendered = render_one(asset("audio", "audio/mpeg", "https://cdn.example.com/a.mp3"), output="markdown")
    assert "<audio controls" in rendered
    assert "https://cdn.example.com/a.mp3" in rendered


def test_render_url():
    rendered = render_one(asset("file", "application/pdf", "https://cdn.example.com/a.pdf"), output="url")
    assert rendered == "https://cdn.example.com/a.pdf"
