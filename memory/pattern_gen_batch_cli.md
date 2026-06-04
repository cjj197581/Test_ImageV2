---
name: pattern-gen-batch-cli
description: "Design pattern for batch image generation CLI tool: read .txt prompts → generate same-name .png → skip existing → fail-fast on quota errors"
metadata: 
  node_type: memory
  type: pattern
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Batch image generation CLI design pattern

The `gen.py` tool pattern for turning a folder of `.txt` prompt files into `.png` images:

### Key design decisions

1. **Same-name convention**: `slide_01.txt` → `slide_01.png`. No timestamp suffixes, no model tags — the filename IS the identity.
2. **Skip existing**: Before calling the API, check if `<name>.png` already exists in the output directory. This saves quota when re-running after partial completion.
3. **Empty file skip**: `.txt` files with no content are silently skipped.
4. **Non-fatal errors**: One image failing (quota, moderation) doesn't abort the whole batch. Collect errors and report at the end.
5. **CLI, not config**: The folder path is a positional argument, not a config file. Simple to use from CMD.

### CLI interface

```bash
python gen.py <folder> [--size WxH] [--out dir] [--model M] [--quality Q] [--verbose]
```

Default: `--size 1792x1024`, `--model gpt-image-2`, `--quality high`.

### Output location logic

- If `--out` specified: all PNGs go there
- If not: PNGs go into the prompt folder itself (alongside the `.txt` files)

### Batch script integration

```batch
@chcp 65001 >nul
python gen.py "中文文件夹"
PAUSE
```

Save as GBK, not UTF-8 (see `feedback-windows-bat-encoding`).

### Pricing awareness

- `high` quality: ~$0.21/image, 130-240s — final delivery
- `medium` quality: ~$0.05/image, 25-40s — review drafts
- `low` quality: ~$0.006/image, 3-8s — rapid prototyping

**Recommended workflow**: low quality first → verify layout/text → high quality for final.

Related: [[feedback-windows-bat-encoding]] [[feedback-windows-unicode-print]]
