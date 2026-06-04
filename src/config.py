"""配置加载模块 —— 从 .env 文件读取 API Key 和 Base URL."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_KEY: str = os.getenv("API_KEY", "")
BASE_URL: str = os.getenv("BASE_URL", "https://api.chatanywhere.com.cn")

# ── 模型变体 ──────────────────────────────────────────────────────────────

MODEL_OFFICIAL = "gpt-image-2"       # 官方直连, token 计费
MODEL_ALL = "gpt-image-2-all"        # 官逆 Web 线, $0.03/张
MODEL_VIP = "gpt-image-2-vip"        # 官逆 Codex 线, $0.03/张, 支持 30 档尺寸

# ── 画质 (仅 gpt-image-2 官方模型) ────────────────────────────────────────

QUALITY_LOW = "low"          # 3-8s,   $0.006  — 缩略图/原型
QUALITY_MEDIUM = "medium"    # 25-40s, $0.053  — 电商/社媒
QUALITY_HIGH = "high"        # 200s+,  $0.211  — 海报/印刷/文字密集
QUALITY_AUTO = "auto"        # 自动选择 (官方默认)

QUALITY_SPEED_MAP = {
    QUALITY_LOW: "3-8s",
    QUALITY_MEDIUM: "25-40s",
    QUALITY_HIGH: "200-240s",
    QUALITY_AUTO: "auto",
}

# ── 输出格式 ──────────────────────────────────────────────────────────────

FORMAT_PNG = "png"
FORMAT_JPEG = "jpeg"
FORMAT_WEBP = "webp"

# ── 响应格式 (gpt-image-2-vip 支持 url, 其他模型仅 b64_json) ─────────────

RESPONSE_B64 = "b64_json"    # base64 图片数据 (默认)
RESPONSE_URL = "url"          # HTTP URL (有效期 1 天, 仅 vip)

# ── 背景 ──────────────────────────────────────────────────────────────────

BACKGROUND_AUTO = "auto"
BACKGROUND_OPAQUE = "opaque"
# 注意: gpt-image-2 不支持 transparent

# ── 图片尺寸 ──────────────────────────────────────────────────────────────

# 官方模型: 边长 ≤3840, 16 的倍数, 宽高比 ≤3:1, 总像素 655,360~8,294,400
# 默认 size="auto" (官方/VIP 都推荐用 auto)
SIZE_AUTO = "auto"

VALID_SIZES = [
    "3072x1024",  # 3:1
    "2048x1024",  # 2:1
    "1792x1024",  # 16:9
    "1536x1024",  # 3:2
    "1360x1024",  # 4:3
    "1024x1024",  # 1:1
    "1024x1360",  # 3:4
    "1024x1536",  # 2:3
    "1024x1792",  # 9:16
    "1024x2048",  # 1:2
    "1024x3072",  # 1:3
]

# 2K/4K (官方模型实验性; VIP 正式支持)
SIZES_HD = [
    "2048x2048",  # 2K 正方形
    "2048x1152",  # 2K 宽屏
    "1152x2048",  # 2K 竖屏
    "3840x2160",  # 4K 宽屏
    "2160x3840",  # 4K 竖屏
    "2880x2880",  # 4K 正方形
]

# gpt-image-2-vip 30 档尺寸 (10 比例 × 3 分辨率: 1K Fast / 2K Recommended / 4K Detail)
VIP_SIZES = {
    "1:1":  ["1024x1024", "2048x2048", "2880x2880"],
    "3:2":  ["1536x1024", "2496x1664", "3840x2560"],
    "2:3":  ["1024x1536", "1664x2496", "2560x3840"],
    "4:3":  ["1360x1024", "2304x1728", "3840x2880"],
    "3:4":  ["1024x1360", "1728x2304", "2880x3840"],
    "16:9": ["1792x1024", "2560x1440", "3840x2160"],
    "9:16": ["1024x1792", "1440x2560", "2160x3840"],
    "2:1":  ["2048x1024", "2560x1280", "3840x1920"],
    "1:2":  ["1024x2048", "1280x2560", "1920x3840"],
    "3:1":  ["3072x1024", "3456x1152", "3840x1280"],
}

VIP_SIZES_FLAT: list[str] = [s for group in VIP_SIZES.values() for s in group]

# ── 模型能力矩阵 ──────────────────────────────────────────────────────────

MODEL_CAPABILITIES = {
    MODEL_OFFICIAL: {
        "quality": True,
        "size_param": True,
        "4k": True,
        "mask_inpainting": True,
        "image_editing": True,
        "chat_completions": False,
        "response_url": False,
        "b64_prefix": "",    # 纯 base64, 无前缀
        "pricing": "token 计费, $0.006~$0.211/张",
        "speed": "low 3-8s / medium 25-40s / high 200-240s",
        "n_limit": 1,
        "default_size": "auto",
    },
    MODEL_ALL: {
        "quality": False,
        "size_param": False,  # 尺寸通过 prompt 描述
        "4k": False,
        "mask_inpainting": False,
        "image_editing": True,
        "chat_completions": True,
        "response_url": False,
        "b64_prefix": "data:image/png;base64,",  # 带前缀
        "pricing": "$0.03/张 统一价",
        "speed": "30-60s",
        "n_limit": 1,
        "default_size": None,
    },
    MODEL_VIP: {
        "quality": False,
        "size_param": True,   # 支持 30 档固定尺寸!
        "4k": True,            # 4K 正式支持, 不加价
        "mask_inpainting": False,
        "image_editing": True,
        "chat_completions": True,
        "response_url": True,  # 支持 url 响应 (有效期 1 天)
        "b64_prefix": "data:image/png;base64,",  # 带前缀
        "pricing": "$0.03/张 统一价 (含 4K)",
        "speed": "90-150s",
        "n_limit": 1,
        "default_size": "auto",
    },
}

# ── 端点 ──────────────────────────────────────────────────────────────────

ENDPOINT_GENERATIONS = "/v1/images/generations"    # 文生图
ENDPOINT_EDITS = "/v1/images/edits"                # 图片编辑
ENDPOINT_CHAT = "/v1/chat/completions"             # 对话式生图 (vip/all)
ENDPOINT_VIDEOS = "/v1/videos"                     # 视频生成 (异步提交/轮询/下载)

# ── 视频模型 ────────────────────────────────────────────────────────────────

# Sora 2 (OpenAI) — ⚠️ 已关停 (2026年3月), 以下常量仅供历史参考
SORA_VIDEO2 = "sora_video2"                        # 竖屏 720x1280 (已不可用)
SORA_VIDEO2_LANDSCAPE = "sora_video2-landscape"    # 横屏 1280x720 (已不可用)
SORA_VIDEO2_15S = "sora_video2-15s"                # 竖屏 15s (已不可用)
SORA_2 = "sora-2"                                  # 异步端点 (已不可用)
SORA_2_PRO = "sora-2-pro"                          # 1080p 专业级 (已不可用)

# Veo 3.1 (Google DeepMind) — ★ 当前唯一可用的视频模型
VEO_3_1_GENERATE = "veo-3.1-generate-preview"      # 文生视频, ~40s, 已验证可用!
VEO_3_1 = "veo-3.1"                                # 标准版 (需单独开通通道)
VEO_3_1_FAST = "veo-3.1-fast"                      # 快速版 (需单独开通通道)

# 视频时长 (Sora 2)
VIDEO_DURATIONS = ["4", "8", "12", "15"]

# 视频尺寸
VIDEO_SIZE_PORTRAIT = "720x1280"     # 竖屏 (Sora 2 默认)
VIDEO_SIZE_LANDSCAPE = "1280x720"    # 横屏

# 视频模型能力矩阵
VIDEO_CAPABILITIES = {
    SORA_VIDEO2: {
        "duration": "4/8/12/15s",
        "size": VIDEO_SIZE_PORTRAIT,
        "audio": True,
        "image_to_video": True,
        "pricing": "$0.12/次",
        "speed": "2.5-4min",
        "endpoint": "chat/completions (流式) + /v1/videos (异步)",
    },
    SORA_VIDEO2_LANDSCAPE: {
        "duration": "4/8/12/15s",
        "size": VIDEO_SIZE_LANDSCAPE,
        "audio": True,
        "image_to_video": True,
        "pricing": "$0.12/次",
        "speed": "2.5-4min",
        "endpoint": "chat/completions (流式) + /v1/videos (异步)",
    },
    VEO_3_1_FAST: {
        "duration": "固定 8s",
        "size": VIDEO_SIZE_PORTRAIT,
        "audio": True,
        "image_to_video": True,
        "pricing": "$0.15/次",
        "speed": "30-60s",
        "endpoint": "chat/completions (流式) + /v1/videos (异步)",
    },
    SORA_2_PRO: {
        "duration": "4/8/12s",
        "size": "720p/1024p/1080p",
        "audio": True,
        "image_to_video": True,
        "pricing": "$0.30~$0.70/秒",
        "speed": "3-10min",
        "endpoint": "/v1/videos (异步)",
    },
}

# 视频模型默认值
VIDEO_DEFAULT_MODEL = VEO_3_1_FAST  # Sora 2 已关停, 默认用 Veo 3.1 Fast
VIDEO_DEFAULT_SIZE = VIDEO_SIZE_PORTRAIT
VIDEO_DEFAULT_SECONDS = "8"


def validate_config() -> None:
    """验证配置是否完整."""
    if not API_KEY or API_KEY == "your-api-key-here":
        raise ValueError(
            "请先配置 API Key:\n"
            "  1. 复制 .env.example 为 .env\n"
            "  2. 在 .env 中填入你的 API_KEY 和 BASE_URL"
        )
