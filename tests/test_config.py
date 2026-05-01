from oss_asset_upload.config import OssConfig


def test_public_url_uses_custom_base():
    config = OssConfig(
        access_key_id="id",
        access_key_secret="secret",
        endpoint="oss-cn-shanghai.aliyuncs.com",
        region="cn-shanghai",
        bucket="bucket",
        public_base_url="https://cdn.example.com/assets/",
    )

    assert config.public_url("notes/demo image.png") == "https://cdn.example.com/assets/notes/demo%20image.png"


def test_public_url_falls_back_to_bucket_endpoint():
    config = OssConfig(
        access_key_id="id",
        access_key_secret="secret",
        endpoint="oss-cn-shanghai.aliyuncs.com",
        region="cn-shanghai",
        bucket="owenshen-aitool-assets",
    )

    assert config.public_url("notes/a.png") == "https://owenshen-aitool-assets.oss-cn-shanghai.aliyuncs.com/notes/a.png"
