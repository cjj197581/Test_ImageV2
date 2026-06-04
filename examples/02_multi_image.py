"""
示例 2: 多图生成 + 模型对比

gpt-image-2 n 固定为 1，多图需循环调用。
演示三种模型的差异: 官方、all ($0.03)、vip ($0.03, 支持 4K 尺寸)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config, MODEL_OFFICIAL, MODEL_ALL, MODEL_VIP
from src.client import generate_multiple, generate_image
from src.utils import save_images

validate_config()

prompt = "一只可爱的柯基犬在草地上奔跑，蓝天白云，卡通风格"

# ── 方式 1: 官方模型，2 张变体 (token 计费) ────────────────────────────

print("使用官方模型 gpt-image-2 生成 2 张...")
results = generate_multiple(
    prompt=prompt, count=2, model=MODEL_OFFICIAL,
    size="1024x1024",
)
save_images(results, prefix="corgi_official")

# ── 方式 2: gpt-image-2-all，$0.03/张 (不支持 size 参数) ─────────────

print("\n使用 gpt-image-2-all 生成 2 张 ($0.03/张, 30-60s)...")
all_results = []
for i in range(2):
    print(f"  生成中 [{i+1}/2]...")
    r = generate_image(prompt=prompt, model=MODEL_ALL)
    # all 模型不具备 size 参数，尺寸由 prompt 控制
    all_results.append(r)
save_images(all_results, prefix="corgi_all")

# ── 方式 3: gpt-image-2-vip，$0.03/张 (支持 size，含 4K) ─────────────

print("\n使用 gpt-image-2-vip 生成 2 张 ($0.03/张, 90-150s)...")
vip_results = []
sizes = ["1024x1024", "1792x1024"]  # vip 支持 30 档固定尺寸
for i, sz in enumerate(sizes):
    print(f"  生成中 [{i+1}/2] size={sz}...")
    r = generate_image(prompt=prompt, model=MODEL_VIP, size=sz)
    vip_results.append(r)
save_images(vip_results, prefix="corgi_vip")

print("\n完成! 对比三种模型效果、速度和花费")
