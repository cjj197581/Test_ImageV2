"""
示例 9: 图片编辑 —— 基于参考图 + 文字描述生成新图

通过 /v1/images/edits 端点，可以:
1. 单图参考: 提供 1 张参考图 + 文字描述 → 生成新图
2. 多图融合: 提供最多 16 张参考图 → 融合生成
3. Mask 修复: 提供参考图 + Mask 图 → 局部重绘

注意:
- 需要先准备参考图片文件
- gpt-image-2-all 不支持 mask inpainting
- 官方模型的 /edits 端点自动启用高清保真 (high-fidelity)
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config, MODEL_OFFICIAL, MODEL_ALL
from src.client import edit_image, generate_image
from src.utils import save_images

validate_config()

# ── 准备参考图（如果没有参考图，先生成一张）──────────────────────────────

OUTPUT = Path(__file__).resolve().parent.parent / "output"
reference_path = OUTPUT / "reference_input.png"

# 先生成一张参考图
print("Step 1: 生成参考图...")
ref_result = generate_image(
    prompt="一张空白的现代简约风格名片模板，白色背景，中央有几何装饰图案",
    size="1024x1024",
    quality="low",  # low 即可，这只是参考
)
save_images([ref_result], prefix="ref")
reference_path = OUTPUT / f"ref_gpt-image-2_{int(time.time())}_0.png"
# 找到刚保存的文件
saved_refs = sorted(OUTPUT.glob("ref_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
if saved_refs:
    reference_path = saved_refs[0]
    print(f"  参考图已保存: {reference_path.name}")
else:
    print("  警告: 未找到参考图，跳过编辑示例")
    sys.exit(1)

# ── 基于参考图编辑 ────────────────────────────────────────────────────────

print("\nStep 2: 基于参考图编辑 (添加文字和元素)...")

try:
    edit_result = edit_image(
        prompt=(
            "在这张名片模板上添加公司名称'星辰科技'和职位'产品经理'，"
            "使用简洁现代的排版，深蓝色文字，保持整体简约风格"
        ),
        image_paths=[str(reference_path)],
        model=MODEL_OFFICIAL,
        size="1024x1024",
    )

    save_images([edit_result], prefix="edited_card")
    print("\n完成! 对比参考图和编辑后的图片")

except Exception as e:
    err = str(e)
    if any(k in err for k in ("404", "not found", "不支持")):
        print(f"当前服务不支持图片编辑: {e}")
        print("可能原因:")
        print("  1. 中转服务未开放 /v1/images/edits 端点")
        print("  2. 模型不支持编辑功能")
        print("\n替代方案: 使用 generate_image() 并在 prompt 中描述参考图的风格")
    else:
        print(f"编辑失败: {e}")
