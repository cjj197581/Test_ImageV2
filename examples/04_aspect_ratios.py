"""
示例 4: 不同宽高比 + 2K/4K 高清

gpt-image-2 支持多种宽高比，以及最高 4K (3840x2160) 分辨率。
注意: 2K 以上为实验性功能，高画质 4K 可能需要 3-5 分钟。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config
from src.client import generate_image
from src.utils import save_images

validate_config()

# ── 不同宽高比示例 ────────────────────────────────────────────────────────

prompt = "一座未来主义城市的天际线，霓虹灯光，赛博朋克风格，雨天夜晚"

test_sizes = {
    "1792x1024": "宽屏 16:9 —— 视频封面",
    "1024x1024": "正方形 1:1 —— Instagram",
    "1024x1792": "竖屏 9:16 —— 手机壁纸",
}

results = []
for size, desc in test_sizes.items():
    print(f"\n生成 {size} ({desc})...")
    result = generate_image(prompt=prompt, size=size)
    results.append(result)

save_images(results, prefix="city_sizes")

# ── 2K 高清示例（可选，时间较长）─────────────────────────────────────────
# 取消注释以测试:
#
# print("\n生成 2K 高清 (2048x1152)... 可能需要 2-3 分钟")
# result_2k = generate_image(
#     prompt=prompt,
#     size="2048x1152",
#     quality="high",
# )
# save_images([result_2k], prefix="city_2k")

print("\n完成!")
