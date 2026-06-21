"""参考图风格迁移 — 将照片转换为动漫风格.

使用方法:
    python style_transfer.py                          # 吉卜力风格 (默认)
    python style_transfer.py --style shinkai          # 新海诚风格
    python style_transfer.py --style ufotable         # 鬼灭之刃 / Ufotable
    python style_transfer.py --style cyberpunk        # 赛博朋克
    python style_transfer.py --list                   # 列出所有风格

原理:
    通过 /v1/chat/completions 端点，将参考图转为 base64 发送，
    搭配风格描述 prompt，生成动漫风格的图片。
    (API易的 /v1/images/edits 端点返回 400，chat/completions 可行)
"""

import argparse
import base64
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import urlretrieve

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import API_KEY, BASE_URL, MODEL_VIP, validate_config

validate_config()

REF_DIR = Path(r"E:\AI\Test\Test_ImageV2\参考图")
OUTPUT = Path(r"E:\AI\Test\Test_ImageV2\output")
OUTPUT.mkdir(exist_ok=True)

STYLES = {
    "ghibli": {
        "name": "Studio Ghibli (吉卜力/宫崎骏)",
        "prompt": (
            "Redraw this photo as Studio Ghibli anime style. "
            "Warm hand-drawn watercolor look, soft natural golden lighting, "
            "gentle pastel color palette, dreamy atmosphere, "
            "clean cel-shaded outlines, nostalgic and whimsical feeling "
            "like Spirited Away or My Neighbor Totoro. Keep the same composition."
        ),
    },
    "shinkai": {
        "name": "Makoto Shinkai (新海诚)",
        "prompt": (
            "Redraw this photo as Makoto Shinkai anime style. "
            "Photorealistic backgrounds with intense lighting, dramatic lens flares, "
            "vibrant saturated skies with volumetric clouds, ray-traced god rays, "
            "sharp detail, cinematic wide-angle composition. "
            "Like Your Name or Weathering With You. Keep the same composition."
        ),
    },
    "ufotable": {
        "name": "Demon Slayer / Ufotable (鬼灭之刃)",
        "prompt": (
            "Redraw this photo as Ufotable / Demon Slayer anime style. "
            "Sharp precise linework, dynamic lighting, floating particle effects, "
            "bold color contrasts, ukiyo-e inspired visual effects, "
            "cinematic action-movie composition. Keep the same composition."
        ),
    },
    "cyberpunk": {
        "name": "Cyberpunk Edgerunners (赛博朋克边缘行者)",
        "prompt": (
            "Redraw this photo as Cyberpunk Edgerunners anime style by Studio Trigger. "
            "Neon-drenched night palette with pink/cyan/amber highlights, "
            "high contrast gritty cel shading, bold thick outlines, "
            "glitch effects and chromatic aberration, rain-slicked surfaces, "
            "dystopian Night City atmosphere. Keep the same composition."
        ),
    },
    "kyoani": {
        "name": "Kyoto Animation / Violet Evergarden (京阿尼)",
        "prompt": (
            "Redraw this photo as Kyoto Animation anime style. "
            "Extremely delicate and detailed linework, soft ethereal lighting, "
            "gentle warm color palette, subtle gradient shading, "
            "Renaissance-inspired beauty and elegance, emotional atmosphere. "
            "Like Violet Evergarden. Keep the same composition."
        ),
    },
    "onepiece": {
        "name": "One Piece / Eiichiro Oda (海贼王)",
        "prompt": (
            "Redraw this photo as One Piece anime style by Eiichiro Oda. "
            "Bold thick sketchy outlines, exaggerated expressions, "
            "bright saturated primary colors, dynamic action poses, "
            "adventure-filled atmosphere, manga-shaded with speed lines. "
            "Keep the same composition."
        ),
    },
    "jojo": {
        "name": "JoJo / Hirohiko Araki (JOJO的奇妙冒险)",
        "prompt": (
            "Redraw this photo as JoJo's Bizarre Adventure style by Hirohiko Araki. "
            "High-fashion illustration aesthetic, dramatic angular poses, "
            "bold pop-art color palette with heavy contrast, "
            "sculptural muscle definition, stylish manga screentone shading, "
            "flamboyant attitude. Keep the same composition."
        ),
    },
    "aot": {
        "name": "Attack on Titan (进击的巨人)",
        "prompt": (
            "Redraw this photo as Attack on Titan anime style by WIT Studio. "
            "Heavy thick shading lines, muted earthy military color palette, "
            "dramatic harsh shadows, gritty realistic proportions, "
            "intense serious atmosphere. Keep the same composition."
        ),
    },
}


def find_ref_image(folder: Path) -> Path | None:
    """找到文件夹中第一个图片文件."""
    for f in sorted(os.listdir(str(folder))):
        ext = os.path.splitext(f)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            return folder / f
    return None


def transfer_style(image_path: Path, style_key: str) -> Path:
    """将图片转换为指定动漫风格，返回保存路径."""
    style = STYLES[style_key]

    with open(image_path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    ext = os.path.splitext(image_path.name)[1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")

    print(f"Style:    {style['name']}")
    print(f"Image:    {image_path.name} ({len(raw)/1024:.0f}KB)")
    print(f"Endpoint: /v1/chat/completions")
    print(f"Model:    {MODEL_VIP}")
    print(f"Generating (est. 60-90s)...\n")

    t0 = time.time()

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_VIP,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{mime};base64,{b64}"},
                    },
                    {"type": "text", "text": style["prompt"]},
                ],
            }],
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    # 从响应中提取图片 URL
    m = re.search(r"!\[.*?\]\((https?://[^\)]+)\)", content)
    if not m:
        m = re.search(r"(https?://[^\s\)]+\.(?:png|jpg|jpeg|webp))", content)
    if not m:
        raise RuntimeError(f"No image URL in response: {content[:300]}")

    img_url = m.group(1)
    elapsed = time.time() - t0
    print(f"Generated ({elapsed:.0f}s)")
    print(f"Downloading: {img_url[:80]}...")

    # 下载
    time.sleep(2)
    img_resp = requests.get(img_url, timeout=60)
    img_resp.raise_for_status()

    out_path = OUTPUT / f"{style_key}_style.png"
    out_path.write_bytes(img_resp.content)
    print(f"Saved: {out_path} ({len(img_resp.content)/1024:.0f}KB)")
    return out_path


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Photo to anime style transfer")
    p.add_argument(
        "--style", "-s",
        default="ghibli",
        choices=list(STYLES.keys()),
        help="Target anime style (default: ghibli)",
    )
    p.add_argument(
        "--image", "-i",
        default=None,
        help="Path to image file (default: first image in ref folder)",
    )
    p.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available styles",
    )
    p.add_argument(
        "--out", "-o",
        default=None,
        help="Output path (default: output/<style>_style.png)",
    )
    args = p.parse_args()

    if args.list:
        print("Available styles:\n")
        for key, s in STYLES.items():
            print(f"  {key:12s} {s['name']}")
        return

    # 找到参考图
    if args.image:
        ref_path = Path(args.image)
        if not ref_path.exists():
            print(f"ERROR: image not found: {args.image}")
            sys.exit(1)
    else:
        ref_path = find_ref_image(REF_DIR)
        if not ref_path:
            print(f"ERROR: no image found in {REF_DIR}")
            sys.exit(1)

    try:
        result = transfer_style(ref_path, args.style)
        print(f"\nDone! -> {result}")
    except Exception as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
