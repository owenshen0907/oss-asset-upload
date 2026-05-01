from pathlib import Path

from oss_asset_upload.naming import dated_slug_prefix, object_key_for_file, slugify


def test_slugify_ascii_safe():
    assert slugify("Desk Shot 01.PNG") == "desk-shot-01.png"
    assert slugify("你好") == "asset"


def test_dated_slug_prefix():
    assert dated_slug_prefix("notes", "x-day-one", "2026-05-02") == "notes/2026/05/x-day-one"


def test_object_key_includes_sha8(tmp_path: Path):
    source = tmp_path / "Desk Shot.PNG"
    source.write_bytes(b"hello")

    key = object_key_for_file(source, prefix="notes/2026/05/demo")

    assert key == "notes/2026/05/demo/desk-shot-2cf24dba.png"
