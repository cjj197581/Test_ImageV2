"""API 客户端封装 —— 支持生成、编辑、对话式生图端点."""

from __future__ import annotations

import json
import re
import time
from typing import Any

import requests
from openai import OpenAI

from .config import (
    API_KEY,
    BASE_URL,
    MODEL_OFFICIAL,
    MODEL_ALL,
    MODEL_VIP,
    QUALITY_AUTO,
    FORMAT_PNG,
    SIZE_AUTO,
    RESPONSE_B64,
    RESPONSE_URL,
    ENDPOINT_CHAT,
)

_ROOT_URL = re.sub(r"/v\d+$", "", BASE_URL) if BASE_URL.endswith("/v1") else BASE_URL


def _client() -> OpenAI:
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def _cap(model: str) -> dict:
    """获取模型能力（延迟导入避免循环）."""
    from .config import MODEL_CAPABILITIES

    return MODEL_CAPABILITIES.get(model, MODEL_CAPABILITIES[MODEL_OFFICIAL])


# ═══════════════════════════════════════════════════════════════════════════
# 端点 1: /v1/images/generations — 文生图
# ═══════════════════════════════════════════════════════════════════════════


def generate_image(
    prompt: str,
    model: str = MODEL_OFFICIAL,
    size: str | None = None,
    quality: str | None = None,
    output_format: str = FORMAT_PNG,
    output_compression: int | None = None,
    response_format: str | None = None,
    seed: int | None = None,
    background: str | None = None,
    moderation: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """文生图.

    Args:
        prompt: 图片描述，支持中文，最长 ~1000 字符
        model: gpt-image-2 / gpt-image-2-all / gpt-image-2-vip
        size: 输出尺寸。官方默认 "auto"，不传则用模型默认值。
              gpt-image-2: 支持任意宽高比 (16的倍数, ≤3:1, ≤3840px)
              gpt-image-2-vip: 支持 30 档预设 (1K/2K/4K)
              gpt-image-2-all: 不支持此参数，通过 prompt 控制
        quality: low/medium/high/auto (仅 gpt-image-2 官方)
        output_format: png/jpeg/webp (默认 png)
        output_compression: 0-100 (仅 jpeg/webp)
        response_format: "b64_json"(默认) 或 "url" (仅 gpt-image-2-vip)
        seed: 随机种子
        background: auto/opaque (不支持 transparent)
        moderation: auto/low

    Returns:
        {"b64_json": "...", "model": "...", "size": "...", "usage": ...}
    """
    caps = _cap(model)
    client = _client()

    # 智能默认值: 官方/VIP 默认 auto, all 不传 size
    if size is None:
        size = caps.get("default_size") or SIZE_AUTO
    if quality is None and caps.get("quality"):
        quality = QUALITY_AUTO

    extra_body: dict[str, Any] = {}
    if seed is not None:
        extra_body["seed"] = seed
    if quality:
        extra_body["quality"] = quality
    if output_format != FORMAT_PNG:
        extra_body["output_format"] = output_format
    if output_compression is not None:
        extra_body["output_compression"] = output_compression
    if background:
        extra_body["background"] = background
    if moderation:
        extra_body["moderation"] = moderation

    params: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
    }
    # gpt-image-2-all 不支持 size 参数
    if caps.get("size_param", True):
        params["size"] = size
    if extra_body:
        params["extra_body"] = extra_body

    # gpt-image-2-vip 支持 response_format
    if response_format and caps.get("response_url"):
        params["response_format"] = response_format

    resp = client.images.generate(**params, **kwargs)

    data = resp.data[0]
    result: dict[str, Any] = {
        "b64_json": data.b64_json or data.url or "",
        "model": model,
        "size": size,
    }
    # vip 模型返回 url 时也有 url 字段
    if data.url and data.url.startswith("http"):
        result["url"] = data.url
    if hasattr(resp, "usage"):
        result["usage"] = resp.usage.dict() if hasattr(resp.usage, "dict") else resp.usage
    return result


def generate_multiple(
    prompt: str,
    count: int = 4,
    model: str = MODEL_OFFICIAL,
    size: str | None = None,
    quality: str | None = None,
    seed: int | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """生成多张图片（循环调用）."""
    results: list[dict[str, Any]] = []
    for i in range(count):
        print(f"  生成中 [{i+1}/{count}]...")
        result = generate_image(
            prompt=prompt, model=model, size=size,
            quality=quality, seed=seed, **kwargs,
        )
        results.append(result)
        if i < count - 1:
            time.sleep(0.5)
    return results


# ═══════════════════════════════════════════════════════════════════════════
# 端点 2: /v1/images/edits — 图片编辑 (参考图 / 融合 / Mask)
# ═══════════════════════════════════════════════════════════════════════════


def edit_image(
    prompt: str,
    image_paths: list[str],
    mask_path: str | None = None,
    model: str = MODEL_OFFICIAL,
    size: str | None = None,
    quality: str | None = None,
    output_format: str = FORMAT_PNG,
    output_compression: int | None = None,
    seed: int | None = None,
    background: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """图片编辑: 基于参考图 + 文字描述生成新图.

    三种模式:
    1. 单图参考: image_paths 传 1 个文件 → 参考风格生成
    2. 多图融合: image_paths 最多 16 个文件 → 融合 (Prompt 中用 "图1/图2" 指代)
    3. Mask 修复: 指定 mask_path → 局部重绘 (仅官方, mask 需 alpha 通道)

    注意: gpt-image-2 编辑自动开启 high-fidelity，不要传 input_fidelity 参数！

    Args:
        prompt: 编辑描述，用 "图1"/"图2" 指代上传顺序中的图片
        image_paths: 参考图路径列表 (png/jpg/webp, 每张 ≤10MB, 最多 16 张)
        mask_path: Alpha 通道 mask 图 (仅对第一张 image 生效, ≤50MB)
        model: 模型名 (官方支持 mask, vip/all 不支持)
        size: 输出尺寸
        quality: low/medium/high/auto
        output_format: png/jpeg/webp
        output_compression: 0-100 (jpeg/webp)
        seed: 随机种子
        background: auto/opaque

    Returns:
        {"b64_json": "...", "model": "...", "size": "..."}
    """
    import os as _os

    caps = _cap(model)
    if size is None:
        size = caps.get("default_size") or SIZE_AUTO
    if quality is None and caps.get("quality"):
        quality = QUALITY_AUTO

    extra_body: dict[str, Any] = {}
    if seed is not None:
        extra_body["seed"] = seed
    if quality:
        extra_body["quality"] = quality
    if output_format != FORMAT_PNG:
        extra_body["output_format"] = output_format
    if output_compression is not None:
        extra_body["output_compression"] = output_compression
    if background:
        extra_body["background"] = background
    # 注意: 不要传 input_fidelity！gpt-image-2 自动开启

    files_data: list[tuple[str, tuple[str, bytes, str]]] = []
    for i, path in enumerate(image_paths):
        filename = _os.path.basename(path)
        ext = _os.path.splitext(path)[1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(
            ext, "image/png"
        )
        with open(path, "rb") as f:
            files_data.append((f"image[{i}]", (filename, f.read(), mime)))

    if mask_path:
        filename = _os.path.basename(mask_path)
        with open(mask_path, "rb") as f:
            files_data.append(("mask", (filename, f.read(), "image/png")))

    url = f"{BASE_URL}/images/edits"
    form_fields: dict[str, str] = {
        "model": model,
        "prompt": prompt,
        "n": "1",
    }
    if caps.get("size_param", True):
        form_fields["size"] = size
    if extra_body:
        form_fields["extra_body"] = json.dumps(extra_body)

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {API_KEY}"},
        data=form_fields,
        files=files_data,
        timeout=300,
    )
    resp.raise_for_status()
    result = resp.json()
    img_data = result["data"][0]
    return {
        "b64_json": img_data.get("b64_json", img_data.get("url", "")),
        "model": model,
        "size": size,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 端点 3: /v1/chat/completions — 对话式生图 (vip / all 专属)
# ═══════════════════════════════════════════════════════════════════════════


def chat_generate(
    prompt: str,
    model: str = MODEL_VIP,
    size: str | None = None,
    system_prompt: str | None = None,
    temperature: float = 0.8,
    **kwargs: Any,
) -> dict[str, Any]:
    """通过 Chat Completions 端点生图 (gpt-image-2-vip / gpt-image-2-all).

    优势:
    - 支持多轮对话连续改图
    - 支持在对话中传入参考图 URL
    - 更自然的交互方式

    仅 vip 和 all 模型支持，官方 gpt-image-2 不支持此端点。

    Args:
        prompt: 图片描述（用户消息）
        model: gpt-image-2-vip 或 gpt-image-2-all
        size: 输出尺寸 (仅 vip, all 通过 prompt 描述)
        system_prompt: 系统提示词
        temperature: 温度 0-1

    Returns:
        {"b64_json": "...", "model": "...", "messages": [...]}
    """
    caps = _cap(model)
    if not caps.get("chat_completions"):
        raise ValueError(f"模型 {model} 不支持 /v1/chat/completions 端点，请用 vip 或 all")

    if size is None and caps.get("size_param"):
        size = caps.get("default_size") or SIZE_AUTO

    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    user_content: str | list[dict] = prompt
    # 如果 prompt 中包含尺寸指令 (vip 模型), 追加
    if size and caps.get("size_param"):
        user_content = f"{prompt}\n\n输出尺寸: {size}"

    messages.append({"role": "user", "content": user_content})

    client = _client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )

    choice = resp.choices[0]
    content = choice.message.content or ""

    # 尝试从响应中提取 base64 图片
    b64_json = ""
    # chat 响应可能是图片 markdown 或直接的 base64
    if content:
        b64_json = content

    return {
        "b64_json": b64_json,
        "model": model,
        "size": size or "N/A",
        "messages": messages,
        "response_content": content,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 端点 4: /draw/completions — 流式 / WebHook (实验性, 见原实现)
# ═══════════════════════════════════════════════════════════════════════════


def draw_completion(
    prompt: str,
    model: str = MODEL_OFFICIAL,
    size: str | None = None,
    seed: int | None = None,
    webhook: str | None = None,
    shut_progress: bool = False,
    timeout: int = 120,
    **kwargs: Any,
) -> dict[str, Any]:
    """通过 /draw/completions 端点生成（非流式，部分服务不支持）."""
    from .config import SIZE_AUTO

    if size is None:
        size = SIZE_AUTO
    url = f"{_ROOT_URL}/draw/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload: dict[str, Any] = {
        "model": model, "prompt": prompt, "size": size, "n": 1, **kwargs,
    }
    if seed is not None:
        payload["seed"] = seed
    if webhook:
        payload["webHook"] = webhook
        payload["shutProgress"] = shut_progress

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "")
    if "text/html" in ct:
        raise RuntimeError("中转服务不支持 /draw/completions，请用 generate_image()")
    return resp.json()


def draw_completion_stream(
    prompt: str,
    model: str = MODEL_OFFICIAL,
    size: str | None = None,
    seed: int | None = None,
    timeout: int = 120,
    **kwargs: Any,
):
    """流式生成（部分服务不支持）."""
    from .config import SIZE_AUTO

    if size is None:
        size = SIZE_AUTO
    url = f"{_ROOT_URL}/draw/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload: dict[str, Any] = {
        "model": model, "prompt": prompt, "size": size, "n": 1,
        "stream": True, **kwargs,
    }
    if seed is not None:
        payload["seed"] = seed

    with requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "")
        if "text/html" in ct:
            raise RuntimeError("中转服务不支持 /draw/completions，请用 generate_image()")
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break
            try:
                yield json.loads(data_str)
            except json.JSONDecodeError:
                continue


# ═══════════════════════════════════════════════════════════════════════════
# 带重试
# ═══════════════════════════════════════════════════════════════════════════


def generate_with_retry(
    prompt: str,
    max_retries: int = 3,
    delay: float = 2.0,
    **kwargs: Any,
) -> dict[str, Any]:
    """带重试的图片生成."""
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            return generate_image(prompt=prompt, **kwargs)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
    raise last_err  # type: ignore[misc]
