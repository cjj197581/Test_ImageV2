"""
示例 3: 种子 (Seed) 控制 —— 保持风格一致

通过固定 seed 参数，可以让多次生成的图片保持相同的风格。
适合做系列作品（电商产品图、漫画系列等）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config
from src.client import generate_image
from src.utils import save_images

validate_config()

# ── 固定种子，生成风格一致的多张图片 ─────────────────────────────────────

seed = 42  # 相同 seed + 相同 prompt = 几乎相同的图片
# 改变 prompt 中的主体但保持风格描述一致

variations = [
    "一只可爱的黑猫坐在沙发上，暖色调插画风格",
    "一只可爱的白猫坐在沙发上，暖色调插画风格",
    "一只可爱的橘猫坐在沙发上，暖色调插画风格",
]

results = []
for i, prompt in enumerate(variations):
    print(f"\n[{i+1}/{len(variations)}] 生成: {prompt}")
    result = generate_image(
        prompt=prompt,
        size="1024x1024",
        seed=seed,
    )
    results.append(result)

save_images(results, prefix="cat_style")

print("\n完成! 观察 3 张图片的风格一致性")
