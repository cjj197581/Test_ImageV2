"""视频生成客户端 —— Sora 2 / Veo 3.1 文本转视频、图片转视频.

两种调用方式:
  方式 1 (同步流式): POST /v1/chat/completions + stream=True → 实时进度 → 下载视频
  方式 2 (异步轮询): POST /v1/videos → 轮询 GET /v1/videos/{id} → 下载视频

注意:
  - 视频生成可能需要 API易 账户单独开通，不属于默认分组
  - 如遇到 "no available channels" 错误，请在 apiyi.com 后台检查分组配置
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import requests

from .config import (
    API_KEY,
    BASE_URL,
    VIDEO_DEFAULT_MODEL,
    VIDEO_DEFAULT_SIZE,
    VIDEO_DEFAULT_SECONDS,
)

_OUTPUT = Path(__file__).resolve().parent.parent / "output"
_OUTPUT.mkdir(exist_ok=True)


class VideoUnavailableError(Exception):
    """视频生成服务不可用 (账户未开通/分组无通道/服务暂不可用)."""
    pass


class VideoChannelError(VideoUnavailableError):
    """当前账户分组没有视频模型通道，需在 API易 后台配置."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 方式 1: 同步流式 (Chat Completions + SSE)
# ═══════════════════════════════════════════════════════════════════════════


def _check_video_response(resp: requests.Response) -> None:
    """检查视频 API 响应，将账户/通道错误转为友好异常."""
    if resp.status_code == 503:
        try:
            body = resp.json()
            msg = body.get("error", {}).get("message", "")
        except Exception:
            msg = ""
        if "no available channels" in msg:
            raise VideoChannelError(
                "API易 当前分组没有视频模型通道。\n"
                "请登录 apiyi.com → 分组管理 → 确保分组包含视频模型 (sora-2 / veo-3.1)。"
            )
        raise VideoUnavailableError(
            f"视频服务暂不可用 (503)。{msg}"
        )
    resp.raise_for_status()


def generate_video_sync(
    prompt: str,
    model: str = VIDEO_DEFAULT_MODEL,
    size: str = VIDEO_DEFAULT_SIZE,
    seconds: str = VIDEO_DEFAULT_SECONDS,
    image_url: str | None = None,
    timeout: int = 600,
    verbose: bool = True,
) -> dict[str, Any]:
    """通过 Chat Completions 端点同步生成视频 (流式 SSE).

    Args:
        prompt: 视频描述
        model: sora_video2 / sora_video2-landscape / veo-3.1-fast 等
        size: 720x1280 (竖屏) 或 1280x720 (横屏)
        seconds: "4" / "8" / "12" / "15" (仅 Sora 2)
        image_url: 可选参考图 URL (图生视频模式)
        timeout: 超时秒数 (默认 10 分钟)
        verbose: 是否打印流式进度

    Returns:
        {"video_url": "...", "model": "...", "size": "...", "local_path": "..."}
    """
    messages = _build_video_messages(prompt, image_url, size)

    if verbose:
        print(f"模型: {model}")
        print(f"尺寸: {size}")
        print(f"时长: {seconds}s")
        print(f"模式: {'图生视频' if image_url else '文生视频'}")
        print(f"正在生成 (预计 2.5-4 分钟)...\n")

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "stream": True,
            "messages": messages,
        },
        stream=True,
        timeout=timeout,
    )
    _check_video_response(resp)

    video_url = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        # SSE 格式: "data: {...}"
        if line.startswith("data: "):
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break
            try:
                event = json.loads(data_str)
                _handle_sse_event(event, verbose)
                url = _extract_video_url(event)
                if url:
                    video_url = url
            except json.JSONDecodeError:
                continue

    if not video_url:
        raise RuntimeError("流式响应中未提取到视频 URL")

    if verbose:
        print(f"\n视频 URL: {video_url}")

    # 下载到本地
    local_path = _download_video(video_url, prefix="video_sync")
    if verbose:
        print(f"本地路径: {local_path}")

    return {
        "video_url": video_url,
        "model": model,
        "size": size,
        "local_path": str(local_path),
    }


def _build_video_messages(
    prompt: str,
    image_url: str | None,
    size: str,
) -> list[dict[str, Any]]:
    """构建视频生成的 Chat messages."""
    full_prompt = f"{prompt}\n\n输出视频尺寸: {size}"

    if image_url:
        return [{
            "role": "user",
            "content": [
                {"type": "text", "text": full_prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }]
    else:
        return [{"role": "user", "content": full_prompt}]


def _handle_sse_event(event: dict, verbose: bool) -> None:
    """处理单个 SSE 事件."""
    if not verbose:
        return

    etype = event.get("type", "")
    if etype == "progress":
        pct = event.get("progress", 0)
        msg = event.get("message", "")
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"\r  Progress: [{bar}] {pct}%  {msg}", end="", flush=True)
    elif etype == "status":
        print(f"\n  Status: {event.get('status', '')} - {event.get('message', '')}")
    elif etype == "error":
        print(f"\n  Error: {event.get('message', '')}")


def _extract_video_url(event: dict) -> str | None:
    """从 SSE 事件中提取视频 URL."""
    # 常见字段名: url / video_url / data.url / choices[0].delta.content
    for key in ("video_url", "url"):
        val = event.get(key)
        if val and isinstance(val, str) and val.startswith("http"):
            return val

    # 可能嵌套在 data 字段中
    data = event.get("data", {})
    if isinstance(data, dict):
        for key in ("video_url", "url"):
            val = data.get(key)
            if val and isinstance(val, str) and val.startswith("http"):
                return val

    # 可能嵌套在 choices 中
    choices = event.get("choices", [])
    if choices:
        content = choices[0].get("delta", {}).get("content", "")
        if content and content.startswith("http"):
            return content

    return None


# ═══════════════════════════════════════════════════════════════════════════
# 方式 2: 异步提交 + 轮询 (/v1/videos)  [生产环境推荐]
# ═══════════════════════════════════════════════════════════════════════════


def submit_video_task(
    prompt: str,
    model: str = "sora-2",
    size: str = VIDEO_DEFAULT_SIZE,
    seconds: str = VIDEO_DEFAULT_SECONDS,
    image_path: str | None = None,
    timeout: int = 30,
) -> str:
    """提交视频生成任务到 /v1/videos, 返回 video_id.

    Args:
        prompt: 视频描述
        model: sora-2 / veo-3.1 等
        size: 1280x720 或 720x1280
        seconds: "4" / "8" / "12" (仅 Sora)
        image_path: 可选参考图路径 (图生视频)
        timeout: 提交超时

    Returns:
        video_id 字符串
    """
    data: dict[str, str] = {
        "model": model,
        "prompt": prompt,
        "seconds": seconds,
        "size": size,
    }

    url = f"{BASE_URL}/videos"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    files = None
    if image_path:
        filename = Path(image_path).name
        files = {
            "input_reference": (filename, open(image_path, "rb"), "image/png"),
        }

    url = f"{BASE_URL}/videos"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    if files:
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=timeout)
    else:
        headers["Content-Type"] = "application/json"
        resp = requests.post(url, headers=headers, json=data, timeout=timeout)
    _check_video_response(resp)
    result = resp.json()
    return result["id"]


def poll_video_status(video_id: str, timeout: int = 30) -> dict[str, Any]:
    """查询视频任务状态.

    Returns:
        {"status": "queued|processing|completed|failed", "progress": 0-100, ...}
    """
    resp = requests.get(
        f"{BASE_URL}/videos/{video_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def wait_for_video(
    video_id: str,
    poll_interval: int = 15,
    max_wait: int = 600,
    verbose: bool = True,
) -> dict[str, Any]:
    """轮询等待视频任务完成.

    Args:
        video_id: 任务 ID
        poll_interval: 轮询间隔秒数
        max_wait: 最大等待秒数
        verbose: 是否打印进度

    Returns:
        完成后的状态 dict, 包含 url 字段
    """
    start = time.time()
    last_pct = -1

    while True:
        elapsed = time.time() - start
        if elapsed > max_wait:
            raise TimeoutError(f"视频生成超时 ({max_wait}s), video_id={video_id}")

        status = poll_video_status(video_id)
        state = status.get("status", "")

        if verbose:
            pct = status.get("progress", 0)
            if pct != last_pct:
                bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
                print(f"\r  Progress: [{bar}] {pct}%  [{state}]  {elapsed:.0f}s", end="", flush=True)
                last_pct = pct

        if state == "completed":
            if verbose:
                print()
            # 等待几秒让内容端点准备好 (避免竞态条件)
            time.sleep(3)
            return status
        elif state == "failed":
            raise RuntimeError(f"视频生成失败: {status.get('error', '未知错误')}")

        time.sleep(poll_interval)


def download_video_content(video_id: str, timeout: int = 120, retries: int = 5) -> bytes:
    """从 /v1/videos/{id}/content 下载视频文件.

    注意: 此端点直接返回 video/mp4 二进制数据, 不是 JSON!
    任务完成后可能需要几秒才能获取内容，内置重试机制。

    Returns:
        视频文件字节数据 (MP4)
    """
    last_error = ""
    for attempt in range(retries):
        resp = requests.get(
            f"{BASE_URL}/videos/{video_id}/content",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=timeout,
        )
        resp.raise_for_status()

        ct = resp.headers.get("content-type", "")
        if "video/" in ct and len(resp.content) > 1000:
            return resp.content

        # 可能是 JSON 错误或竞态条件 — 等待后重试
        if attempt < retries - 1:
            import time as _time
            _time.sleep(3)
        last_error = resp.text[:200]

    raise RuntimeError(f"视频内容获取失败 (重试{retries}次): {last_error}")


def generate_video_async(
    prompt: str,
    model: str = "sora-2",
    size: str = VIDEO_DEFAULT_SIZE,
    seconds: str = VIDEO_DEFAULT_SECONDS,
    image_path: str | None = None,
    poll_interval: int = 15,
    max_wait: int = 600,
    verbose: bool = True,
) -> dict[str, Any]:
    """异步生成视频 (提交 + 轮询 + 下载).

    这是生产环境推荐的工作流。

    Args:
        prompt: 视频描述
        model: sora-2 / veo-3.1 等
        size: 1280x720 或 720x1280
        seconds: "4" / "8" / "12"
        image_path: 可选参考图路径 (图生视频)
        poll_interval: 轮询间隔秒数
        max_wait: 最大等待秒数
        verbose: 是否打印进度

    Returns:
        {"video_url": "...", "local_path": "...", "video_id": "...", ...}
    """
    if verbose:
        print(f"模型: {model}")
        print(f"尺寸: {size}")
        print(f"时长: {seconds}s")
        print(f"模式: {'图生视频' if image_path else '文生视频'}")
        print()

    # Step 1: 提交任务
    if verbose:
        print("Step 1/3: 提交任务...")
    video_id = submit_video_task(
        prompt=prompt, model=model, size=size,
        seconds=seconds, image_path=image_path,
    )
    if verbose:
        print(f"  任务 ID: {video_id}")

    # Step 2: 轮询等待
    if verbose:
        print("Step 2/3: 等待生成 (每 {}s 查询)...".format(poll_interval))
    result = wait_for_video(
        video_id, poll_interval=poll_interval,
        max_wait=max_wait, verbose=verbose,
    )

    # Step 3: 下载
    if verbose:
        print("Step 3/3: 下载视频...")
    video_bytes = download_video_content(video_id)
    local_path = _save_video_bytes(video_bytes, video_id)
    if verbose:
        print(f"  本地路径: {local_path}")

    return {
        "video_id": video_id,
        "video_url": result.get("url", ""),
        "local_path": str(local_path),
        "model": model,
        "size": size,
        "duration": result.get("duration", seconds),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 内部工具
# ═══════════════════════════════════════════════════════════════════════════


def _download_video(url: str, prefix: str = "video") -> Path:
    """下载视频到 output/ 目录."""
    timestamp = int(time.time())
    ext = ".mp4"
    filepath = _OUTPUT / f"{prefix}_{timestamp}{ext}"
    urlretrieve(url, filepath)
    size_kb = filepath.stat().st_size / 1024
    print(f"  文件大小: {size_kb:.0f}KB")
    return filepath


def _save_video_bytes(data: bytes, video_id: str) -> Path:
    """保存视频字节到 output/ 目录."""
    timestamp = int(time.time())
    short_id = video_id[:12] if len(video_id) > 12 else video_id
    filepath = _OUTPUT / f"video_async_{short_id}_{timestamp}.mp4"
    filepath.write_bytes(data)
    size_kb = len(data) / 1024
    print(f"  文件大小: {size_kb:.0f}KB")
    return filepath
