"""
示例 7: WebHook 异步模式（生产环境推荐）

通过 /draw/completions 端点的 WebHook 模式提交异步任务。

注意: API易 不支持此端点，会自动降级为标准同步调用。
      如需 WebHook，推荐诗云API (shuyunapi.com)。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import validate_config
from src.client import draw_completion, generate_image
from src.utils import save_images

validate_config()

WEBHOOK_URL = "https://webhook.site/your-unique-id"

print("WebHook 异步模式")
print("=" * 50)
print()
print("生产环境工作流: 提交任务 -> 等待回调 -> 接收图片")
print(f"当前回调 URL: {WEBHOOK_URL}")
print()

try:
    result = draw_completion(
        prompt="一幅山水画风格的中国风景，远山、松树、云雾，传统水墨画风",
        size="1024x1024",
        webhook=WEBHOOK_URL,
        shut_progress=True,
        timeout=30,
    )
    print(f"任务已提交! 返回: {result}")

except Exception as e:
    err = str(e)
    if any(k in err for k in ("404", "not found", "html", "不支持", "draw/completions")):
        print("当前中转服务不支持 /draw/completions 端点")
        print("改用标准 generate_image() 同步生成...\n")

        result = generate_image(
            prompt="一幅山水画风格的中国风景，远山、松树、云雾，传统水墨画风",
            size="1024x1024",
        )
        save_images([result], prefix="webhook_fallback")
        print("\n已用标准端点完成 (降级方案)")
        print("如需 WebHook 功能，推荐诗云API (shuyunapi.com)")
    else:
        print(f"调用失败: {e}")
