# oss-asset-upload

Small CLI for uploading local content assets to Alibaba Cloud OSS and returning Markdown-ready URLs.

The first use case is the `AiTool-content` writing workflow: keep Markdown in Git, keep binary files out of the content repository, and reference public OSS URLs from notes.

## Local Install

```bash
cd /Users/shenting/.local/share/codex-tools/oss-asset-upload
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
cp .env.example .env
```

Edit `.env` with your OSS credentials and bucket settings.

The stable local command for Codex skills is:

```bash
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload
```

## Configuration

Required:

```env
OSS_ACCESS_KEY_ID=...
OSS_ACCESS_KEY_SECRET=...
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_REGION=cn-shanghai
OSS_BUCKET=owenshen-aitool-assets
```

Recommended:

```env
OSS_ASSET_PREFIX=notes
OSS_PUBLIC_BASE_URL=https://your-cdn-or-custom-domain.example.com
OSS_CACHE_CONTROL=public, max-age=31536000, immutable
```

If `OSS_PUBLIC_BASE_URL` is omitted, URLs are rendered as:

```text
https://<bucket>.<endpoint>/<object-key>
```

## Usage

Upload one image for a note:

```bash
oss-asset-upload upload ./desk-shot.png --slug x-day-one --date 2026-05-02
```

Output:

```md
![desk shot](https://owenshen-aitool-assets.oss-cn-shanghai.aliyuncs.com/notes/2026/05/x-day-one/desk-shot-a91f22c0.png)
```

Upload audio and render HTML for Markdown:

```bash
oss-asset-upload upload ./narration.mp3 --slug x-day-one --output html
```

Dry-run without uploading:

```bash
oss-asset-upload upload ./image.png --slug draft-note --dry-run --output json
```

Use an explicit OSS prefix:

```bash
oss-asset-upload upload ./image.png --prefix notes/2026/05/x-day-one
```

For convenience, the command also accepts files without the `upload` subcommand:

```bash
oss-asset-upload ./image.png --slug draft-note
```

## Object Key Policy

Default key format:

```text
notes/YYYY/MM/<slug>/<safe-basename>-<sha8>.<ext>
```

Example:

```text
notes/2026/05/x-day-one/desk-shot-a91f22c0.png
```

Why this policy:

- Date and slug keep assets grouped by article.
- Lowercase ASCII filenames avoid URL and Markdown portability issues.
- The SHA-256 prefix prevents accidental collisions and allows long-lived cache headers.
- The original binary file never needs to be committed to the content repository.

## Bucket Recommendation

Recommended bucket name for AiTool content assets:

```text
owenshen-aitool-assets
```

Recommended region:

```text
cn-shanghai
```

Recommended object prefixes:

```text
notes/YYYY/MM/<slug>/        # published note assets
notes/drafts/<slug>/         # draft assets if you want separation
raw/YYYY/MM/                 # temporary raw material
```

Keep one bucket for public content assets, then use prefixes for organization. Do not create one bucket per article.

## Skill Integration

A Codex skill should call the local CLI instead of reimplementing OSS upload logic:

```bash
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload upload "$FILE" --slug "$POST_SLUG" --date "$POST_DATE" --output markdown
```

The skill can then insert the returned Markdown or HTML into `AiTool-content/posts/*.md`.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

## License

MIT
