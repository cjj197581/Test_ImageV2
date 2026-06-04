"""
示例 11: Veo 3.1 批量文本转视频 —— 异步并发 (生产环境推荐)

同时提交两个任务，并发轮询，提高效率。

优势:
  - 并发提交多个任务，总耗时接近单个任务
  - 失败不扣费，可以安心重试
  - 适合批量生产场景

模型: veo-3.1-generate-preview
预计耗时: 40-60s (并发)
价格: ~$0.15-$0.25/次 × 任务数
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    validate_config,
    VEO_3_1_GENERATE,
    VIDEO_SIZE_PORTRAIT,
    VIDEO_SIZE_LANDSCAPE,
)
from src.video_client import (
    submit_video_task,
    wait_for_video,
    download_video_content,
    VideoChannelError,
    VideoUnavailableError,
)

validate_config()

try:
    # ═══════════════════════════════════════════════════════════════════════════
    # Step 1: 并发提交两个任务
    # ═══════════════════════════════════════════════════════════════════════════

    print("=" * 60)
    print("Veo 3.1 Batch Video Generation (2 concurrent tasks)")
    print("=" * 60)
    print()
    print("Step 1: Submitting 2 tasks concurrently...")

    task1_id = submit_video_task(
        prompt=(
            "一只橘猫蹲在窗台上，窗外飘着雪花，壁炉的火光在房间里摇曳，"
            "温暖的室内与寒冷的窗外形成对比，猫咪悠闲地摇着尾巴，"
            "电影级灯光，温馨氛围"
        ),
        model=VEO_3_1_GENERATE,
        size=VIDEO_SIZE_PORTRAIT,
    )
    print(f"  Task 1: {task1_id} (portrait, cat in snow)")

    task2_id = submit_video_task(
        prompt=(
            "一艘未来主义的飞船缓缓驶过霓虹灯闪烁的赛博朋克城市天际线，"
            "雨夜，街道反射着五彩斑斓的灯光，镜头跟随飞船平移，"
            "远处有巨大的全息广告牌，电影级科幻画面"
        ),
        model=VEO_3_1_GENERATE,
        size=VIDEO_SIZE_LANDSCAPE,
    )
    print(f"  Task 2: {task2_id} (landscape, cyberpunk)")

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 2: 轮询等待两个任务完成
    # ═══════════════════════════════════════════════════════════════════════════

    print()
    print("Step 2: Waiting for both tasks...")
    start = time.time()

    # wait_for_video 会阻塞，所以用更短的轮询间隔并发检查
    import requests
    from src.config import API_KEY, BASE_URL

    tasks = {
        task1_id: {"label": "Task 1 (cat)", "done": False, "result": None},
        task2_id: {"label": "Task 2 (cyberpunk)", "done": False, "result": None},
    }

    while not all(t["done"] for t in tasks.values()):
        for tid, info in tasks.items():
            if info["done"]:
                continue
            resp = requests.get(
                f"{BASE_URL}/videos/{tid}",
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=15,
            )
            data = resp.json()
            status = data.get("status", "")
            pct = data.get("progress", 0)

            if status == "completed":
                info["done"] = True
                info["result"] = data
                print(f"  [{info['label']}] COMPLETED ({time.time()-start:.0f}s)")
            elif status == "failed":
                info["done"] = True
                info["result"] = data
                print(f"  [{info['label']}] FAILED ({time.time()-start:.0f}s)")

        # 打印进度
        pending = [f"{t['label']}" for t in tasks.values() if not t["done"]]
        if pending:
            print(f"\r  Waiting: {', '.join(pending)}  [{time.time()-start:.0f}s]", end="", flush=True)
        if any(not t["done"] for t in tasks.values()):
            time.sleep(10)

    print()
    print(f"  Total wait: {time.time()-start:.0f}s")

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 3: 下载视频
    # ═══════════════════════════════════════════════════════════════════════════

    print()
    print("Step 3: Downloading videos...")

    paths = []
    for tid, info in tasks.items():
        if info["result"] and info["result"].get("status") == "completed":
            video_bytes = download_video_content(tid)
            from src.video_client import _save_video_bytes
            path = _save_video_bytes(video_bytes, tid)
            paths.append(path)
            print(f"  [{info['label']}] {path}")
        else:
            print(f"  [{info['label']}] Skipped (failed)")

    print(f"\n{'=' * 60}")
    print("Batch complete!")
    print(f"{'=' * 60}")
    for p in paths:
        print(f"  {p}")

except VideoChannelError as e:
    print(f"\n[Channel Error] {e}")
except VideoUnavailableError as e:
    print(f"\n[Service Unavailable] {e}")
except Exception as e:
    print(f"\n[Error] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
