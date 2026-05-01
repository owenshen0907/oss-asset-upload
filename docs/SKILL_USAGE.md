# Codex Skill Usage Contract

The skill should treat this repository as the single uploader implementation.

## Stable Executable

```text
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload
```

## Required Inputs

- Local file path.
- Post slug or explicit prefix.
- Optional date from Markdown frontmatter.
- Desired output format: `markdown`, `html`, `url`, or `json`.

## Recommended Calls

For an image in a note:

```bash
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload upload "$FILE" --slug "$SLUG" --date "$DATE" --output markdown
```

For audio/video where HTML figures are preferred:

```bash
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload upload "$FILE" --slug "$SLUG" --date "$DATE" --output html
```

For metadata-driven editing:

```bash
/Users/shenting/.local/share/codex-tools/oss-asset-upload/.venv/bin/oss-asset-upload upload "$FILE" --slug "$SLUG" --date "$DATE" --output json
```
