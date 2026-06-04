"""
示例 6: 流式响应 —— 实时获取生成进度

通过 /draw/completions 端点的 stream 模式，
可以在图片生成过程中实时收到进度更新。

注意: API易 (apiyi.com) 目前不支持此端点，
      会自动降级为标准 generate_image()。
      完整流式功能可尝试诗云API (shuyunapi.com)。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config
from src.client import draw_completion_stream, generate_image
from src.utils import save_images

validate_config()

# ── 流式调用（带降级）─────────────────────────────────────────────────────

print("尝试流式生成图片...\n")

try:
    urls_found: list[str] = []

    for event in draw_completion_stream(
        prompt="一只可爱的折耳猫戴着眼镜在看书，温暖的台灯光，细腻插画",
        size="1024x1024",
        timeout=30,
    ):
        event_type = event.get("type", "unknown")
        print(f"  [事件] 类型: {event_type}")
        if "url" in event:
            urls_found.append(event["url"])
            print(f"  -> 获取到图片: {event['url'][:60]}...")

    if urls_found:
        print(f"\n流式生成完成，共获取 {len(urls_found)} 张图片")
    else:
        print("\n流式完成但未获取到图片数据")

except Exception as e:
    err = str(e)
    if any(k in err for k in ("404", "not found", "html", "不支持", "draw/completions")):
        print("当前中转服务不支持 /draw/completions 端点")
        print("改用标准 generate_image() 生成...\n")

        result = generate_image(
            prompt="一只可爱的折耳猫戴着眼镜在看书，温暖的台灯光，细腻插画",
            size="1024x1024",
        )
        save_images([result], prefix="fallback_cat")
        print("\n已用标准端点完成生成 (降级方案)")
    else:
        print(f"流式调用失败: {e}")
