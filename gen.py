"""批量文生图工具 —— 将文件夹中的 .txt prompt 文件批量生成 PNG 图片.

Usage:
    python gen.py <prompts_folder> [--size WxH] [--out <output_folder>] [--model MODEL] [--quality QUALITY]

Examples:
    python gen.py "需要生成的图片的提示词"
    python gen.py "需要生成的图片的提示词" --size 1024x1024
    python gen.py "需要生成的图片的提示词" --size 1792x1024 --out ./output
    python gen.py "需要生成的图片的提示词" --model gpt-image-2-vip --quality low

默认:
    --size   1792x1024  (16:9 横版)
    --out    与 .txt 同目录
    --model  gpt-image-2 (官方模型，中文文字最优)
    --quality high
"""

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import MODEL_OFFICIAL, MODEL_VIP, MODEL_ALL, QUALITY_HIGH, QUALITY_LOW, QUALITY_MEDIUM
from src.client import generate_image
from src.utils import decode_b64


# ── 默认值 ──────────────────────────────────────────────────────────────────
DEFAULT_SIZE = "1792x1024"

DEFAULT_MODEL = MODEL_OFFICIAL
DEFAULT_QUALITY = QUALITY_HIGH
VALID_MODELS = [MODEL_OFFICIAL, MODEL_VIP, MODEL_ALL]
VALID_QUALITIES = [QUALITY_HIGH, QUALITY_MEDIUM, QUALITY_LOW]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Batch text-to-image: convert .txt prompts in a folder to PNG images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gen.py
  python gen.py "prompts"
  python gen.py "prompts" --size 1024x1024
  python gen.py "prompts" --size 1792x1024 --out ./slides
  python gen.py "prompts" --model gpt-image-2-vip --quality low
        """,
    )
    p.add_argument(
        "folder",
        help="Path to folder containing .txt prompt files",
    )
    p.add_argument(
        "--size",
        default=DEFAULT_SIZE,
        help=f"Output image size, e.g. 1792x1024 (16:9), 1024x1024 (1:1). Default: {DEFAULT_SIZE}",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Output folder for generated PNGs. Default: same folder as .txt files",
    )
    p.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=VALID_MODELS,
        help=f"Model to use. Default: {DEFAULT_MODEL}",
    )
    p.add_argument(
        "--quality",
        default=DEFAULT_QUALITY,
        choices=VALID_QUALITIES,
        help=f"Image quality (gpt-image-2 only). Default: {DEFAULT_QUALITY}",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # ── 验证文件夹 ───────────────────────────────────────────────────────
    folder_name = args.folder
    folder = Path(folder_name)
    if not folder.is_absolute():
        folder = (Path(__file__).resolve().parent / folder).resolve()
    else:
        folder = folder.resolve()

    if not folder.is_dir():
        print(f"ERROR: folder not found: {folder}")
        sys.exit(1)

    # ── 收集 .txt 文件 ───────────────────────────────────────────────────
    txt_files = sorted(
        [folder / f for f in os.listdir(str(folder))
         if f.endswith(".txt") and os.path.isfile(os.path.join(str(folder), f))]
    )
    if not txt_files:
        print(f"No .txt files found in: {folder}")
        sys.exit(1)

    # ── 输出目录 ─────────────────────────────────────────────────────────
    out_dir = Path(args.out).resolve() if args.out else folder
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 显示配置 ─────────────────────────────────────────────────────────
    print(f"Folder:   {folder}")
    print(f"Output:   {out_dir}" + (" (same as source)" if args.out is None else ""))
    print(f"Model:    {args.model}")
    print(f"Size:     {args.size}")
    print(f"Quality:  {args.quality}")
    print(f"Files:    {len(txt_files)} .txt prompt(s)\n")
    print("=" * 60)

    # ── 逐个生成 ─────────────────────────────────────────────────────────
    succeeded = []
    failed = []
    t_start = time.time()

    for i, txt_path in enumerate(txt_files, 1):
        name = txt_path.stem  # filename without .txt

        # 跳过已存在的 PNG
        existing = out_dir / f"{name}.png"
        if existing.exists():
            print(f"[{i}/{len(txt_files)}] {name} -> SKIP (already exists: {existing})")
            succeeded.append(existing)
            continue

        prompt = txt_path.read_text(encoding="utf-8").strip()
        if not prompt:
            print(f"[{i}/{len(txt_files)}] {name} -> SKIP (empty file)")
            continue

        print(f"[{i}/{len(txt_files)}] {name} ({len(prompt)} chars) ... ", end="", flush=True)
        t0 = time.time()

        try:
            result = generate_image(
                prompt=prompt,
                model=args.model,
                size=args.size,
                quality=args.quality,
            )

            # 解码并直接保存到指定路径
            b64_data = result.get("b64_json", "")
            if not b64_data:
                raise RuntimeError("no b64_json in response")

            img_bytes, ext = decode_b64(b64_data)
            png_path = out_dir / f"{name}.png"
            png_path.write_bytes(img_bytes)

            elapsed = time.time() - t0
            size_kb = len(img_bytes) / 1024
            print(f"OK ({elapsed:.0f}s, {size_kb:.0f}KB)")
            succeeded.append(png_path)

            if args.verbose:
                print(f"         -> {png_path}")

        except Exception as e:
            elapsed = time.time() - t0
            err_msg = str(e)[:200]
            print(f"FAIL ({elapsed:.0f}s)")
            print(f"         {err_msg}")
            failed.append((name, err_msg))

    # ── 汇总 ─────────────────────────────────────────────────────────────
    t_total = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"Done! {len(succeeded)} ok, {len(failed)} fail ({t_total:.0f}s total)")
    print(f"{'=' * 60}")

    if succeeded:
        print(f"\nGenerated ({len(succeeded)}):")
        for p in succeeded:
            size_kb = p.stat().st_size / 1024
            print(f"  {p.name} ({size_kb:.0f}KB)")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name, err in failed:
            print(f"  {name}: {err}")

    if not succeeded:
        sys.exit(1)


if __name__ == "__main__":
    main()
