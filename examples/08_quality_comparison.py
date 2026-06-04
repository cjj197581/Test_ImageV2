"""
示例 8: 画质对比 —— low / medium / high

gpt-image-2 官方模型支持 quality 参数:

  quality   |  速度      | 1024x1024 价格 | 适用
  ----------|------------|---------------|----------
  low       |  3-8s      | $0.006        | 预览/原型/批量
  medium    |  25-40s    | $0.053        | 电商/社媒/文章
  high      |  200-240s  | $0.211        | 海报/印刷/文字密集
  auto      |  自动      | 自动           | 默认推荐

注意: gpt-image-2-all 和 gpt-image-2-vip 不支持 quality。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    validate_config,
    QUALITY_LOW,
    QUALITY_MEDIUM,
    QUALITY_HIGH,
    QUALITY_SPEED_MAP,
)
from src.client import generate_image
from src.utils import save_images

validate_config()

prompt = "一只金毛犬戴着红色领结坐在复古皮椅上，暖色调棚拍光，精致细节"
results = []

for quality in [QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH]:
    expected = QUALITY_SPEED_MAP[quality]
    print(f"\n{'='*50}")
    print(f"画质: {quality} (预计 {expected})")
    print(f"{'='*50}")

    start = time.time()
    result = generate_image(
        prompt=prompt,
        size="1024x1024",
        quality=quality,
    )
    elapsed = time.time() - start
    result["_quality"] = quality
    result["_elapsed"] = f"{elapsed:.0f}s"
    results.append(result)
    print(f"  实际耗时: {elapsed:.0f}s")

# ── 汇总 ─────────────────────────────────────────────────────────────────

print(f"\n{'='*50}")
print("画质对比汇总:")
print(f"{'='*50}")
for r in results:
    print(f"  {r['_quality']:7s} | 耗时: {r['_elapsed']:>6s}")

save_images(results, prefix="quality_test")

print("\n建议: 日常测试用 low, 正式出图用 high")
