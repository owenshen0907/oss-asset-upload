"""Command line interface for oss-asset-upload."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .config import ConfigError, load_config
from .naming import dated_slug_prefix
from .render import render_many
from .uploader import OssAssetUploader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-asset-upload",
        description="Upload local files to Alibaba Cloud OSS and print Markdown-ready URLs.",
    )
    parser.add_argument("--version", action="store_true", help="Show package version and exit.")

    subparsers = parser.add_subparsers(dest="command")
    upload = subparsers.add_parser("upload", help="Upload one or more local files.")
    upload.add_argument("files", nargs="+", type=Path, help="Local files to upload.")
    upload.add_argument("--env-file", help="Path to a .env file with OSS_* settings.")
    upload.add_argument("--bucket", help="Override OSS_BUCKET.")
    upload.add_argument("--endpoint", help="Override OSS_ENDPOINT, for example oss-cn-shanghai.aliyuncs.com.")
    upload.add_argument("--region", help="Override OSS_REGION.")
    upload.add_argument("--public-base-url", help="Override OSS_PUBLIC_BASE_URL.")
    upload.add_argument("--prefix", help="Object key prefix. Defaults to OSS_ASSET_PREFIX or notes.")
    upload.add_argument("--slug", help="Append YYYY/MM/<slug> under the prefix, useful for one article.")
    upload.add_argument("--date", help="Date for --slug in YYYY-MM-DD format. Defaults to today.")
    upload.add_argument(
        "--output",
        choices=["markdown", "html", "url", "json"],
        default="markdown",
        help="Output format printed after upload.",
    )
    upload.add_argument("--caption", help="Caption/alt text to use in rendered Markdown or HTML.")
    upload.add_argument("--no-hash", action="store_true", help="Do not append the file SHA-256 prefix to object names.")
    upload.add_argument("--forbid-overwrite", action="store_true", help="Ask OSS to reject writes when the object key exists.")
    upload.add_argument("--cache-control", help="Override Cache-Control header for uploaded objects.")
    upload.add_argument("--dry-run", action="store_true", help="Compute keys and URLs without uploading.")
    return parser


def _rewrite_argv_for_default_upload(argv: Sequence[str]) -> list[str]:
    if not argv:
        return []
    first = argv[0]
    known = {"upload", "-h", "--help", "--version"}
    if first in known or first.startswith("-"):
        return list(argv)
    return ["upload", *argv]


def run_upload(args: argparse.Namespace) -> int:
    config = load_config(
        env_file=args.env_file,
        bucket=args.bucket,
        endpoint=args.endpoint,
        region=args.region,
        public_base_url=args.public_base_url,
        prefix=args.prefix,
    )
    prefix = dated_slug_prefix(args.prefix or config.asset_prefix, args.slug, args.date)
    uploader = OssAssetUploader(config)

    assets = []
    for path in args.files:
        prepared = uploader.prepare_asset(path, prefix=prefix, include_hash=not args.no_hash)
        uploaded = uploader.upload_asset(
            prepared,
            cache_control=args.cache_control,
            forbid_overwrite=args.forbid_overwrite,
            dry_run=args.dry_run,
        )
        assets.append(uploaded)

    print(render_many(assets, output=args.output, caption=args.caption))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    from . import __version__

    parser = build_parser()
    rewritten = _rewrite_argv_for_default_upload(list(argv if argv is not None else sys.argv[1:]))
    args = parser.parse_args(rewritten)

    if args.version:
        print(__version__)
        return 0

    if args.command == "upload":
        try:
            return run_upload(args)
        except ConfigError as exc:
            print(f"config error: {exc}", file=sys.stderr)
            return 2
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - CLI should return a readable failure.
            status = getattr(exc, "status_code", None)
            message = getattr(exc, "message", None)
            if status or message:
                print(f"oss error: {message or exc} (HTTP {status or 500})", file=sys.stderr)
            else:
                print(f"error: {exc}", file=sys.stderr)
            return 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
