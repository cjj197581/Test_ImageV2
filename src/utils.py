"""工具函数 —— 解码、保存图片."""

from __future__ import annotations

import base64
import re
import time
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def decode_b64(data: str) -> tuple[bytes, str]:
    """解码 base64 图片数据，兼容两种格式.

    gpt-image-2 (官方):   纯 base64 "iVBORw0KGgo..."
    gpt-image-2-all (官逆): 带 data: 前缀 "data:image/png;base64,iVBORw0..."

    Returns:
        (图片字节数据, 扩展名如 "png")
    """
    ext = "png"
    if data.startswith("data:"):
        # "data:image/png;base64,iVBORw0..." 或 "data:image/jpeg;base64,..."
        header, b64 = data.split(",", 1)
        m = re.search(r"image/(\w+)", header)
        if m:
            ext = m.group(1)
            if ext == "jpeg":
                ext = "jpg"
        return base64.b64decode(b64), ext
    else:
        # 纯 base64
        try:
            return base64.b64decode(data), ext
        except Exception:
            return data.encode(), "txt"


def save_images(
    results: list[dict[str, Any]],
    prefix: str = "image",
) -> list[Path]:
    """批量保存生成结果到 output/ 目录.

    Args:
        results: generate_image() 或 generate_multiple() 的返回列表
                 每个元素是 {"b64_json": "...", "model": "...", ...}
        prefix: 文件名前缀

    Returns:
        保存的文件路径列表
    """
    paths: list[Path] = []
    timestamp = int(time.time())
    for i, result in enumerate(results):
        b64_data = result.get("b64_json", "")
        if not b64_data:
            print(f"  [{i+1}/{len(results)}] 跳过: 无图片数据")
            continue

        img_bytes, ext = decode_b64(b64_data)
        model = result.get("model", "")
        # gpt-image-2-all 模型名含斜杠时会取最后一段
        model_tag = model.rsplit("/", 1)[-1] if model else "img"
        filepath = OUTPUT_DIR / f"{prefix}_{model_tag}_{timestamp}_{i}.{ext}"
        filepath.write_bytes(img_bytes)
        paths.append(filepath)
        print(f"  [{i+1}/{len(results)}] {filepath.name} "
              f"({len(img_bytes)/1024:.0f}KB)")

    return paths


def download_image(url: str, filepath: Path) -> Path:
    """从 URL 下载图片到本地."""
    if url.startswith("data:"):
        img_bytes, _ = decode_b64(url)
        filepath.write_bytes(img_bytes)
    elif url.startswith("http://") or url.startswith("https://"):
        urlretrieve(url, filepath)
    else:
        img_bytes, _ = decode_b64(url)
        filepath.write_bytes(img_bytes)
    return filepath


def open_images(paths: list[Path]) -> None:
    """用默认图片查看器打开图片列表."""
    for p in paths:
        if p.exists():
            Image.open(p).show()
