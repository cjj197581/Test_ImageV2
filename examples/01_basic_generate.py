"""
示例 1: 基础文本转图片

最简单的用法 —— 输入一段描述文字，生成一张图片。
gpt-image-2 默认 quality=auto, 自动平衡速度和质量。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config
from src.client import generate_image
from src.utils import save_images

validate_config()

# ── 生成图片 ──────────────────────────────────────────────────────────────

print("正在生成图片 (quality=auto, 约 30-60s)...")

result = generate_image(
    prompt="一只可爱的橙色虎斑猫坐在窗台上，阳光从窗外照进来，温暖的午后氛围",
    size="1024x1024",
)

print(f"模型: {result['model']}, 尺寸: {result['size']}")

# ── 保存到本地 ────────────────────────────────────────────────────────────

save_images([result], prefix="cat")

print("\n完成! 图片已保存到 output/ 目录")
