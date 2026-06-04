---
name: feedback-windows-bat-encoding
description: .bat files MUST be saved as GBK/ANSI (not UTF-8); @chcp 65001 >nul switches console to UTF-8 for output only
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Windows CMD batch file encoding rule

`.bat` files on Chinese Windows have **two encoding layers**:

1. **File parse encoding**: CMD parses the `.bat` file using the system's default ANSI code page — **GBK (cp936)** on Chinese Windows. If the `.bat` is saved as UTF-8 (especially with BOM), CMD will mangle Chinese characters BEFORE executing any command.
2. **Console output encoding**: `chcp 65001` switches the console code page to UTF-8, but it only affects output AFTER it's executed.

**This means the first line `@chcp 65001 >nul` itself must survive GBK parsing.** If the file is UTF-8, CMD reads garbage before `chcp` even runs.

## Correct recipe

```batch
@chcp 65001 >nul
cd /d "E:\path\to\project"
python script.py "中文文件夹"
pause
```

- Save the file with **GBK/ANSI encoding** (Windows Notepad default)
- `@chcp 65001 >nul` — first line, switches console to UTF-8 for Python output
- Chinese in the `.bat` body (after `chcp`) will display correctly AND the file parses correctly

## Wrong approaches

| Approach | Result |
|----------|--------|
| UTF-8 with BOM | `'���' is not recognized as a command` |
| UTF-8 without BOM | Same — CMD uses system ANSI regardless |
| Writing `.bat` from Python with `encoding='utf-8'` | Broken on Chinese Windows |
| Writing `.bat` from Python with `encoding='gbk'` | Works |

## Writing .bat from Python

```python
with open('run.bat', 'w', encoding='gbk') as f:
    f.write(bat_content)
```

Or write raw bytes to avoid any encoding conversion:

```python
with open('run.bat', 'wb') as f:
    f.write(bat_content.encode('gbk'))
```

Related: [[feedback-windows-unicode-print]]
