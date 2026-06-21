# CLAUDE.md — Test_ImageV2 项目说明书

## 项目概述

基于 API易 (apiyi.com) 中转服务的 AI 图像与视频生成 Python 实战项目。

- **图片生成**: OpenAI gpt-image-2 系列 (3 个模型变体)
- **视频生成**: Google Veo 3.1 (`veo-3.1-generate-preview`)
- **批量工具**: `gen.py` — 通用 CLI，将文件夹中的 `.txt` 批量生成 `.png`
- **风格迁移**: `style_transfer.py` — 参考图 → 8 种动漫风格

## 快速命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行单个示例
python examples/01_basic_generate.py

# 批量生成 (核心工具)
python gen.py "文件夹路径" [--size 1792x1024] [--model gpt-image-2] [--quality high]

# 风格迁移
python style_transfer.py --style ghibli

# 运行所有测试 (无自动测试框架, 逐个运行 examples/)
```

## 项目架构

```
src/
├── config.py          # 环境变量、模型常量、能力矩阵
├── client.py          # 图片生成客户端 (3 个 API 端点)
├── utils.py           # 解码/保存/下载工具
└── video_client.py    # 视频生成客户端 (异步工作流)

examples/              # 11 个递进学习脚本 (01~09 图片, 10~11 视频)
gen.py                 # 通用批量文生图 CLI ★
style_transfer.py      # 参考图动漫风格迁移 (8 种风格)
batch_slides.py        # 课件专用批量脚本 (过渡, 路径写死)
run_gen2.bat           # gen.py 一键启动 (GBK 编码)

memory/                # 20 个经验记忆文件 (从开发中总结)
```

## src/config.py 关键导出

```python
from src.config import (
    API_KEY, BASE_URL,          # 从 .env 加载
    MODEL_OFFICIAL,             # "gpt-image-2"
    MODEL_VIP,                  # "gpt-image-2-vip"
    MODEL_ALL,                  # "gpt-image-2-all"
    VEO_3_1_GENERATE,           # "veo-3.1-generate-preview" (唯一可用的视频模型)
    QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH, QUALITY_AUTO,
    FORMAT_PNG, FORMAT_JPEG, FORMAT_WEBP,
    VIDEO_SIZE_PORTRAIT,        # "720x1280"
    VIDEO_SIZE_LANDSCAPE,       # "1280x720"
    VIDEO_DEFAULT_SECONDS,      # "8"
    MODEL_CAPABILITIES,         # 图片模型能力矩阵
    VIDEO_CAPABILITIES,         # 视频模型能力矩阵
    VIP_SIZES,                  # VIP 模型 30 档预设尺寸
    validate_config,            # 校验 API_KEY 是否存在
)
```

### BASE_URL 注意
`BASE_URL` 已包含 `/v1`（如 `https://api.apiyi.com/v1`），拼接端点时勿再加 `/v1` 前缀：
- ✅ `f"{BASE_URL}/images/generations"` → `.../v1/images/generations`
- ❌ `f"{BASE_URL}/v1/images/generations"` → `.../v1/v1/images/generations`

## src/client.py 关键函数

```python
from src.client import generate_image, edit_image, generate_chat

# 文生图 — 端点: /v1/images/generations
result = generate_image(
    prompt="...",
    model="gpt-image-2",     # MODEL_OFFICIAL / MODEL_VIP / MODEL_ALL
    size="1792x1024",        # 默认 "auto", gpt-image-2-all 不支持此参数
    quality="high",          # 仅官方模型支持
    seed=42,                 # 通过 extra_body 传递
)
# → {"b64_json": "...", "model": "...", "size": "..."}

# 图片编辑 — 端点: /v1/images/edits (API易 上返回 400)
edit_image(prompt="...", image_paths=["ref.png"], model=...)

# 对话式生图 — 端点: /v1/chat/completions (仅 VIP/ALL 支持)
generate_chat(prompt="...", image_urls=["https://..."], model=MODEL_VIP)
```

### 核心规则: extra_body 传参
seed / quality / output_format / output_compression / background / moderation
必须通过 `extra_body` 传递，不能直接作为 SDK 参数：
```python
extra_body={"seed": 42, "quality": "high", "background": "opaque"}
```

### 模型能力差异
| 能力 | gpt-image-2 | gpt-image-2-vip | gpt-image-2-all |
|------|:---:|:---:|:---:|
| quality 参数 | ✅ | ❌ | ❌ |
| size 参数 | ✅ 任意 | ✅ 30档 | ❌ |
| chat/completions | ❌ | ✅ | ✅ |
| base64 格式 | 纯 b64 | data: 前缀 | data: 前缀 |

## src/utils.py 关键函数

```python
from src.utils import decode_b64, save_images, download_image

# 解码 base64 (兼容 纯b64 和 data:URI 两种格式)
img_bytes, ext = decode_b64(data)  # → (bytes, "png")

# 批量保存
save_images([result1, result2], prefix="cat")
# → output/cat_gpt-image-2_1779882309_0.png

# 从 URL 下载
download_image("https://...", Path("output/img.png"))
```

## src/video_client.py 关键函数

```python
from src.video_client import (
    generate_video_async,    # 推荐: 提交→轮询→下载 一步到位
    submit_video_task,       # 提交任务 → video_id
    wait_for_video,          # 轮询等待 → status_dict
    download_video_content,  # 下载 MP4 → bytes
    VideoChannelError,       # 通道未配置
    VideoUnavailableError,   # 服务不可用
)

result = generate_video_async(
    prompt="mountain sunrise...",
    model=VEO_3_1_GENERATE,     # "veo-3.1-generate-preview"
    size=VIDEO_SIZE_LANDSCAPE,  # "1280x720"
    seconds="4",
    poll_interval=10,           # 轮询间隔
    max_wait=600,               # 最大等待 10 分钟
)
# → {"video_id": "...", "video_url": "...", "local_path": "..."}
```

### 视频关键细节
- **仅异步可用**: `POST /v1/videos` → 轮询 `GET /v1/videos/{id}` → 下载 `GET /v1/videos/{id}/content`
- **同步流式不可用**: Chat Completions SSE 返回 HTML
- **竞态条件**: status=completed 后必须等 3s 才能取 content，内置 5x 重试
- **content 返回二进制**: Content-Type: `video/mp4`，非 JSON
- **中文审核风险**: 复杂中文 prompt 可能在 50% 进度时静默失败，建议用英文

## 关键经验 (开发中踩过的坑)

1. **extra_body**: seed/quality/output_format/background/moderation 必须通过 extra_body 传递
2. **base64 双格式**: 官方模型=纯 b64, VIP/ALL=Data URL (带 `data:image/png;base64,` 前缀)
3. **size 参数**: gpt-image-2-all 不支持 size 参数，按 MODEL_CAPABILITIES 判断
4. **URL 拼接**: BASE_URL 已含 `/v1`，不要再加
5. **中文错误检测**: API易 错误消息中英文混合，fallback 逻辑必须检测 "不支持" "未开放"
6. **/edits 不可用**: 用 `/v1/chat/completions` + base64 image_url 替代
7. **Windows .bat**: 必须用 GBK/ANSI 编码保存；`@chcp 65001` 切换输出编码
8. **Windows print**: 避免 Unicode 符号 (✓✗→…)，用 ASCII 替代 (OK/FAIL/->/...)
9. **VIDEO_DEFAULT_MODEL**: 正确值是 `veo-3.1-generate-preview`，其他变体名 503
10. **视频 content 端点**: 返回 binary MP4，检查 Content-Type + body 大小确认成功

## gen.py 批量工具

```bash
python gen.py <folder> [--size WxH] [--out dir] [--model M] [--quality Q] [--verbose]

# 特性:
# - 同名输出: slide_01.txt → slide_01.png
# - 自动跳过已存在的 PNG
# - 空 .txt 跳过
# - 非致命错误 (一个失败不影响后续)
# - 最后汇总 OK/FAIL

# 默认值:
# --size: 1792x1024 (16:9), --model: gpt-image-2, --quality: high
# --out: 与 .txt 同目录
```

## style_transfer.py 风格迁移

```bash
python style_transfer.py                      # 默认吉卜力
python style_transfer.py --style cyberpunk    # 赛博朋克
python style_transfer.py --image "照片.jpg"   # 指定图片
python style_transfer.py --list               # 列出 8 种风格

# 原理: /v1/chat/completions + base64 image_url
# 注意: 必须用 gpt-image-2-vip (官方模型不支持 chat)
# CDN 下载用 requests 而非 urllib (User-Agent 兼容)
```

## 环境配置

```bash
# .env 文件 (不提交)
API_KEY=sk-你的API易Key
BASE_URL=https://api.apiyi.com/v1
```

## Git 信息

- **仓库**: https://github.com/cjj197581/Test_ImageV2
- **远程**: `git@github.com:cjj197581/Test_ImageV2.git`
- **分支**: `main`
- **用户**: cjj197581 / cjj81@vip.163.com
- **.gitignore**: 排除 .env, __pycache__, API易截图, 参考图/ (含个人隐私)
