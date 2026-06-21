"""批量生成 5 张相控阵雷达教学 PPT 页面 (16:9 横版).

使用 gpt-image-2 官方模型 + high 画质, 确保中文文字清晰可读.
预计每张 200-240s, 总计 ~20 分钟.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, r"E:\AI\Test\Test_ImageV2")

from src.config import MODEL_OFFICIAL, QUALITY_HIGH
from src.client import generate_image
from src.utils import save_images

import os

PROMPTS_DIR = Path(r"E:\AI\Test\Test_ImageV2\需要生成的图片的提示词")

# 读取所有 slide prompt
slide_files = sorted(
    [PROMPTS_DIR / f for f in os.listdir(str(PROMPTS_DIR)) if f.startswith("slide_") and f.endswith(".txt")]
)

print(f"Found {len(slide_files)} prompt files:\n")
for f in slide_files:
    prompt = f.read_text(encoding="utf-8").strip()
    print(f"  {f.name}: {len(prompt)} chars")

print(f"\n{'='*60}")
print("Start batch generation (gpt-image-2 / high / 1792x1024)")
print(f"{'='*60}\n")

results = []
for i, f in enumerate(slide_files, 1):
    prompt = f.read_text(encoding="utf-8").strip()
    name = f.stem  # slide_01, slide_02, ...

    print(f"[{i}/{len(slide_files)}] {name} generating... ({len(prompt)} chars)")
    t0 = time.time()

    try:
        result = generate_image(
            prompt=prompt,
            model=MODEL_OFFICIAL,
            size="1792x1024",
            quality=QUALITY_HIGH,
        )
        paths = save_images([result], prefix=name)
        path = paths[0] if paths else "unknown"
        elapsed = time.time() - t0
        print(f"  OK ({elapsed:.0f}s) -> {path}")
        results.append((name, str(path), True, None))
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAIL ({elapsed:.0f}s): {e}")
        results.append((name, "", False, str(e)))

print(f"\n{'='*60}")
print("Batch generation complete!")
print(f"{'='*60}")
for name, path, ok, err in results:
    status = f"OK {path}" if ok else f"FAIL {err}"
    print(f"  {name}: {status}")
