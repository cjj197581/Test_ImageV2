"""
示例 5: 中文文字渲染

gpt-image-2 一大亮点是中文（日文、韩文等）文字精准渲染，
99% 字符渲染准确率，比上一代大幅提升。

提示: 文字密集型图建议用 quality="high" 以获得最佳效果。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config, QUALITY_HIGH
from src.client import generate_image
from src.utils import save_images

validate_config()

# ── 测试中文文字生成 ─────────────────────────────────────────────────────

test_cases = [
    {
        "prompt": (
            "一张现代简约风格的海报，中央用漂亮的中文艺术字体写着"
            "'春日花语'，背景是粉色樱花和蓝天，柔和光线，4K高清"
        ),
        "prefix": "cn_poster",
    },
    {
        "prompt": (
            "一张产品标签设计图，包含以下中文文字：'纯天然蜂蜜'、"
            "'净含量 500g'、'产地 云南'。自然清新风格，浅黄色背景，"
            "旁边有蜂蜜罐和花朵装饰"
        ),
        "prefix": "cn_label",
    },
    {
        "prompt": (
            "手机应用启动页面，正中间用醒目的中文字体显示应用名称"
            "'每日阅读'，副标题'每天进步一点点'。简洁清新的阅读主题，"
            "书本和咖啡元素"
        ),
        "prefix": "cn_app",
    },
]

results = []
for case in test_cases:
    print(f"\n生成: {case['prompt'][:50]}...")
    result = generate_image(
        prompt=case["prompt"],
        size="1024x1024",
        quality=QUALITY_HIGH,  # 文字密集型，推荐高画质
    )
    results.append(result)

save_images(results, prefix="cn_text")

print("\n完成! 检查图片中的中文文字是否清晰正确")
