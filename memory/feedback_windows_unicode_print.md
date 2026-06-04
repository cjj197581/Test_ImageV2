---
name: feedback-windows-unicode-print
description: Avoid Unicode in Python print() on Windows CMD — ✓✗完成失败 cause UnicodeEncodeError(gbk); use ASCII OK/FAIL instead
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Unicode print() crashes on Windows CMD

On Chinese Windows, `print()` with Unicode characters like `✓` (U+2713), `✗` (U+2717), or even Chinese characters can fail:

```
UnicodeEncodeError: 'gbk' codec can't encode character '✓'
```

**Why:** Python defaults to the console's encoding for stdout, which is **GBK (cp936)** on Chinese Windows. GBK cannot encode `✓` `✗` `→` etc.

## Workarounds

1. **Use ASCII fallbacks** (simplest):
   ```python
   print("OK (163s) -> output.png")     # instead of "✓ 完成 (163s) → output.png"
   print("FAIL (2s): quota exceeded")   # instead of "✗ 失败 (2s): 额度不足"
   ```

2. **Set PYTHONIOENCODING** (environment-level):
   ```batch
   set PYTHONIOENCODING=utf-8
   python script.py
   ```

3. **Reconfigure stdout** (code-level):
   ```python
   import sys
   sys.stdout.reconfigure(encoding='utf-8')
   ```

## Recommendation

For CLI tools that must work reliably on Windows without environment setup, use **approach 1 (ASCII fallbacks)** throughout. It's bulletproof and doesn't require the user to configure anything.

## Characters that cause trouble on GBK

| Character | Unicode | GBK-safe? |
|-----------|---------|-----------|
| `✓` check mark | U+2713 | **No** → use `OK` |
| `✗` x mark | U+2717 | **No** → use `FAIL` |
| `→` arrow | U+2192 | **No** → use `->` |
| `…` ellipsis | U+2026 | **No** → use `...` |
| `—` em dash | U+2014 | **No** → use `--` |
| Most CJK | U+4E00+ | Usually OK (they're in GBK) |

Related: [[feedback-windows-bat-encoding]]
