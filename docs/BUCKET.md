# OSS Bucket Plan

## Recommended Bucket

Use:

```text
owenshen-aitool-assets
```

Rationale:

- `owenshen` makes the globally unique namespace more likely to be available.
- `aitool` ties the bucket to the public site/content system.
- `assets` keeps it broader than only notes, while still avoiding mixed application data.


## Naming Rules

Alibaba Cloud OSS bucket names must be globally unique, use only lowercase letters, digits, and hyphens, start and end with a lowercase letter or digit, and be 3 to 63 characters long. Bucket names cannot be renamed after creation.

Reference: https://www.alibabacloud.com/help/en/oss/user-guide/bucket-naming-conventions

## Region

Use the same region as the existing OSS test project unless you have a reason to split regions:

```text
cn-shanghai
```

## Access Policy

For public note media, use one of these patterns:

1. Public-read bucket for non-sensitive published assets.
2. Private bucket plus CDN/custom domain with controlled public access.

Do not upload private source files, credentials, unpublished sensitive audio, or customer data to a public bucket.

## Prefixes

```text
notes/YYYY/MM/<slug>/        # assets referenced by public Markdown notes
notes/drafts/<slug>/         # optional draft area
raw/YYYY/MM/                 # temporary/generated raw assets
```

## Environment

```env
OSS_BUCKET=owenshen-aitool-assets
OSS_REGION=cn-shanghai
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_ASSET_PREFIX=notes
```
