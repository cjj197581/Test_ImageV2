"""
示例 10: Veo 3.1 文本转视频 —— 异步提交 + 轮询

通过 /v1/videos 端点的三步工作流:
  Step 1: POST /v1/videos       → 提交任务, 获取 task_id
  Step 2: GET  /v1/videos/{id}  → 轮询状态 (每 10s 查一次)
  Step 3: GET  /v1/videos/{id}/content → 下载视频 (直接返回 MP4 二进制)

模型: veo-3.1-generate-preview (已验证可用)
预计耗时: 40-60s
价格: ~$0.15-$0.25/次

注意:
  - Sora 2 已于 2026年3月 被 OpenAI 关停
  - Veo 3.1 固定 8s 视频, 支持同步音频
  - content 端点直接返回 video/mp4 二进制数据
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    validate_config,
    VEO_3_1_GENERATE,
    VIDEO_SIZE_PORTRAIT,
    VIDEO_SIZE_LANDSCAPE,
)
from src.video_client import generate_video_async, VideoChannelError, VideoUnavailableError

validate_config()

try:
    # ═══════════════════════════════════════════════════════════════════════════
    # 测试 1: 竖屏视频 — 温馨场景
    # ═══════════════════════════════════════════════════════════════════════════

    print("=" * 60)
    print("Test 1: Veo 3.1 portrait (720x1280)")
    print("=" * 60)

    result1 = generate_video_async(
        prompt=(
            "一只可爱的柴犬在春天的公园里奔跑，樱花花瓣随风飘落，"
            "温暖的午后阳光透过树叶洒在地面上，慢动作，电影质感"
        ),
        model=VEO_3_1_GENERATE,
        size=VIDEO_SIZE_PORTRAIT,
        seconds="8",
        poll_interval=10,
        max_wait=600,
    )

    print(f"\nTest 1 OK! Video: {result1['local_path']}")

    # ═══════════════════════════════════════════════════════════════════════════
    # 测试 2: 横屏视频 — 自然风光
    # ═══════════════════════════════════════════════════════════════════════════

    print(f"\n{'=' * 60}")
    print("Test 2: Veo 3.1 landscape (1280x720)")
    print("=" * 60)

    result2 = generate_video_async(
        prompt=(
            "海浪轻柔地拍打着白色沙滩，日落时分天空呈现橙色和紫色的渐变，"
            "几只海鸥在远处飞翔，棕榈树的叶子在微风中摇曳，"
            "平静舒缓的氛围，自然纪录片风格"
        ),
        model=VEO_3_1_GENERATE,
        size=VIDEO_SIZE_LANDSCAPE,
        seconds="8",
        poll_interval=10,
        max_wait=600,
    )

    print(f"\nTest 2 OK! Video: {result2['local_path']}")

    print(f"\n{'=' * 60}")
    print("All tests complete!")
    print(f"{'=' * 60}")
    print(f"  Test 1 (portrait):   {result1['local_path']}")
    print(f"  Test 2 (landscape):  {result2['local_path']}")

except VideoChannelError as e:
    print(f"\n[Channel Error] {e}")
except VideoUnavailableError as e:
    print(f"\n[Service Unavailable] {e}")
except Exception as e:
    print(f"\n[Error] {type(e).__name__}: {e}")
