# API易 (apiyi.com) 完整使用指南

> 基于 https://docs.apiyi.com/en 官方文档站全面整理
> 整理日期: 2026-05-27
> 当前使用的 API Key 来源: apiyi.com

---

## 目录

1. [基础信息](#1-基础信息)
2. [文生图 API](#2-文生图-api-text-to-image)
3. [图片编辑 API](#3-图片编辑-api-image-to-image)
4. [文生视频 API](#4-文生视频-api-text-to-video)
5. [图生视频 API](#5-图生视频-api-image-to-video)
6. [所有图片模型对比](#6-图片模型完整对比)
7. [所有视频模型对比](#7-视频模型完整对比)
8. [最佳实践](#8-最佳实践)

---

## 1. 基础信息

### 1.1 Base URL

| 节点 | URL | 用途 |
|------|-----|------|
| 国内主力 | `https://api.apiyi.com/v1` | OpenAI 兼容模型通用 |
| 国内备选 | `https://b.apiyi.com/v1` | 主节点异常时切换 |
| 海外/VIP | `https://vip.apiyi.com/v1` | 高性能/Claude/Gemini |
| Gemini 原生 | `https://api.apiyi.com` (不加 /v1) | Gemini 原生格式 |
| Climate CDN | `https://api-cf.apiyi.com/v1` | 仅文本请求 |

### 1.2 三大端点

| 端点 | Content-Type | 支持的模型 |
|------|-------------|-----------|
| `POST /v1/images/generations` | `application/json` | 所有文生图模型 |
| `POST /v1/images/edits` | `multipart/form-data` | gpt-image-2 / gpt-image-2-all / gpt-image-2-vip / FLUX / Seedream |
| `POST /v1/chat/completions` | `application/json` | gpt-image-2-all / gpt-image-2-vip / Sora / Veo / Gemini |

### 1.3 通用响应格式

```json
{
  "data": [{
    "b64_json": "base64图片数据...",
    "url": "https://r2cdn.copilotbase.com/xxx.png"
  }],
  "created": 1778037127,
  "usage": {
    "input_tokens": 98,
    "output_tokens": 1185,
    "total_tokens": 1283
  }
}
```

- b64_json 格式因模型而异: 官方模型是纯 base64，官逆模型 (-all/-vip) 带 `data:image/png;base64,` 前缀
- URL 有效期: 通常 1 天 (Sora/Veo) 或 24 小时 (gpt-image)，FLUX 仅 10 分钟
- 失败请求不扣费

---

## 2. 文生图 API (Text-to-Image)

API易 提供 **7 个图模型系列，约 20+ 个可选模型**，覆盖所有主流供应商。

### 2.1 gpt-image-2 系列 (OpenAI 官方 + 官逆)

**三条路线，同一 API Key:**

| 模型 | 路线 | 计费 | 速度 | 4K |
|------|------|------|------|-----|
| `gpt-image-2` | OpenAI 官方转发 | Token 计费, $0.006~$0.211/张 | low 3-8s / high 200-240s | 支持 |
| `gpt-image-2-all` | 官逆 (ChatGPT Web线) | **$0.03/张 统一价** | 30-60s | 不支持 |
| `gpt-image-2-vip` | 官逆 (Codex线) | **$0.03/张 统一价** | 90-150s | 支持 (30档尺寸) |

#### 参数 (gpt-image-2 官方)

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.apiyi.com/v1"
)

response = client.images.generate(
    model="gpt-image-2",
    prompt="一只橘猫在秋叶中玩耍，暖色调，4K高清",
    size="1024x1024",         # 或 "auto" (默认)
    quality="auto",           # low / medium / high / auto (默认)
    output_format="png",      # png(默认) / jpeg / webp
    output_compression=85,    # 0-100, 仅 jpeg/webp
    background="auto",        # auto(默认) / opaque (不支持 transparent)
    seed=42,                  # 随机种子
    n=1,                      # 固定为 1
)
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | 是 | — | `gpt-image-2` / `gpt-image-2-all` / `gpt-image-2-vip` |
| `prompt` | string | 是 | — | 图片描述，最长 ~1000 字符，支持中文 |
| `size` | string | 否 | `"auto"` | 官方: 任意 16 倍数, ≤3840px, 宽高比 ≤3:1。all: 不支持此参数，通过 prompt 描述 |
| `quality` | string | 否 | `"auto"` | `low`/`medium`/`high`/`auto`。仅官方模型支持，all/vip 不支持 |
| `output_format` | string | 否 | `"png"` | `png`/`jpeg`/`webp` |
| `output_compression` | int | 否 | — | 0-100，仅 jpeg/webp |
| `background` | string | 否 | `"auto"` | `auto`/`opaque` (不支持透明) |
| `seed` | int | 否 | — | 固定可保持风格一致 |

#### gpt-image-2-vip 30 档尺寸

vip 模型支持 10 种比例 × 3 档分辨率 (1K Fast / 2K Recommended / 4K Detail):

| 比例 | 1K | 2K | 4K |
|------|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 2880x2880 |
| 3:2 | 1536x1024 | 2496x1664 | 3840x2560 |
| 2:3 | 1024x1536 | 1664x2496 | 2560x3840 |
| 4:3 | 1360x1024 | 2304x1728 | 3840x2880 |
| 3:4 | 1024x1360 | 1728x2304 | 2880x3840 |
| 16:9 | 1792x1024 | 2560x1440 | 3840x2160 |
| 9:16 | 1024x1792 | 1440x2560 | 2160x3840 |
| 2:1 | 2048x1024 | 2560x1280 | 3840x1920 |
| 1:2 | 1024x2048 | 1280x2560 | 1920x3840 |
| 3:1 | 3072x1024 | 3456x1152 | 3840x1280 |

#### gpt-image-2 画质与定价

| 画质 | 速度 | 1024x1024 价格 | 适用场景 |
|------|------|---------------|----------|
| `low` | 3-8s | $0.006 | 缩略图、原型、批量预览 |
| `medium` | 25-40s | $0.053 | 电商主图、社媒配图 |
| `high` | 200-240s | $0.211 | 海报、印刷、文字密集型 |
| `auto` | 自动 | 自动 | 默认推荐 |

### 2.2 Gemini / Nano Banana 系列 (Google)

**Nano Banana = Google Gemini Flash 图片生成模型的 API易 代号**

| 模型 ID | 代号 | 价格 | 速度 |
|---------|------|------|------|
| `gemini-3.1-flash-image-preview` | Nano Banana 2 | ~$0.035/张(1K) / $0.07(4K) | 5-25s |
| `gemini-3-pro-image-preview` | Nano Banana Pro | ~$0.05/张 | 10-20s |
| `gemini-2.5-flash-image` | Nano Banana (正式版) | ~$0.025/张 | 5-10s |

#### 参数 (OpenAI 兼容格式)

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",
    base_url="https://vip.apiyi.com/v1"
)

response = client.chat.completions.create(
    model="gemini-3.1-flash-image-preview",
    messages=[{
        "role": "user",
        "content": "一杯拿铁艺术拉花，俯拍视角，木质桌面背景，暖色调"
    }],
    # 通过 extra_body 传入 Gemini 特有参数
    extra_body={
        "imageSize": "2K",           # 512px / 1K(默认) / 2K / 4K
        "aspectRatio": "16:9",       # 14 种比例
        "thinkingLevel": "high",     # minimal(默认) / high
        "includeThoughts": False,    # 是否返回思考过程
    }
)
```

#### 独有功能

- **Image Search Grounding**: 生成前 Google 图片搜索获取真实参考 (Nano Banana 2 独家)
- **Thinking 模式**: minimal/high 推理深度
- **14 种宽高比**: 含 1:4、4:1、1:8、8:1 超宽/超高
- **参考图控制**: 最多 14 个物体参考 + 4 个人物参考
- **多轮对话编辑**: 聊天式迭代优化图片

### 2.3 FLUX 系列 (Black Forest Labs)

7 个活跃模型:

| 模型 ID | 价格 | 速度 | 定位 |
|---------|------|------|------|
| `flux-2-max` | $0.07/张 | <15s | 旗舰 + 网络搜索 |
| `flux-2-pro` | $0.03/张 | <10s | 生产级最佳性价比 |
| `flux-2-flex` | $0.06/张 | 较慢 | 排版调优 |
| `flux-2-klein-9b` | $0.01/张 | <1s | 平衡速度质量 |
| `flux-2-klein-4b` | $0.01/张 | <1s | 最快 (开源 Apache 2.0) |
| `flux-kontext-max` | $0.07/张 | — | 编辑最高质量 |
| `flux-kontext-pro` | $0.035/张 | 5-6s | 编辑性价比之选 |

```python
resp = client.images.generate(
    model="flux-2-pro",
    prompt="A sleek silver sports car on a coastal highway at sunset",
    size="1024x1024",                  # 最高 4MP (2048x2048)
    extra_body={"safety_tolerance": 2} # 0(最严)~6(最宽松)
)
```

#### 独有功能

- **Grounding Search** (flux-2-max): 实时网页搜索，生成"昨天比分/实时天气/历史事件"
- **Hex 颜色控制**: prompt 中用 `#02eb3c` `#ff0088` 指定品牌色
- **32K 超长 prompt**: 支持结构化 JSON 描述
- **URL 仅 10 分钟有效**: 必须立即下载到自有存储

### 2.4 Seedream 系列 (字节跳动)

| 模型 ID | 价格 | 最高分辨率 | 特点 |
|---------|------|-----------|------|
| `seedream-5-0-260128` | $0.035/张 | 3K | 最新版，综合体验最佳 |
| `seedream-4-5-251128` | $0.04/张 | 4K (4096x4096) | 文字渲染突破性提升 |
| `seedream-4-0-250828` | $0.03/张 | 4K | 最实惠的 4K 方案 |

```python
resp = client.images.generate(
    model="seedream-5-0-260128",
    prompt="一张中国风海报，标题'新年快乐'，红色金色配色",
    size="2048x2048",
)
```

#### 独有功能

- **统一生成-编辑**: 同一端点完成文生图和图片编辑
- **批量序列生成**: `sequential_image_generation: "auto"` + `max_images`，单次最多 15 张
- **新用户前 200 张免费** (字节跳动提供)

### 2.5 gpt-image-1 / 1.5 (OpenAI 历史版本)

| 模型 | 价格 (1024x1024) | 状态 |
|------|-----------------|------|
| `gpt-image-1.5` | low $0.009 / high $0.133 | 仍可用，建议升级到 gpt-image-2 |
| `gpt-image-1` | low $0.005 / high $0.036 | 仍可用，建议升级 |
| `gpt-image-1-mini` | 更低 | 仍可用 |

### 2.6 Sora Image (官逆)

- 模型 ID: `sora-image`
- 价格: $0.01/张
- (详细文档较少，主要用于快速出图)

---

## 3. 图片编辑 API (Image-to-Image / Image Editing)

API易 平台支持 **三种图片编辑方式**，分别对应不同的模型和端点:

### 3.1 方式一: /v1/images/edits (multipart/form-data)

**支持模型**: gpt-image-2 (官方) / gpt-image-2-all / gpt-image-2-vip / FLUX / Seedream

```python
import requests

# 单图参考: 基于参考图风格生成新图
with open("reference.png", "rb") as f1:
    resp = requests.post(
        "https://api.apiyi.com/v1/images/edits",
        headers={"Authorization": "Bearer sk-xxx"},
        data={
            "model": "gpt-image-2",
            "prompt": "将这张照片转为水彩画风格，添加中文字'春日'",
            "size": "1024x1024",
            "n": "1",
        },
        files={
            "image[0]": ("ref.png", f1, "image/png"),
        },
        timeout=300
    )
```

#### 三种编辑模式

| 模式 | image[] | mask | prompt 示例 |
|------|---------|------|------------|
| **单图参考** | 1 张 | 无 | "把这张照片变成动漫风格" |
| **多图融合** | 2-16 张 | 无 | "融合图1的风格和图2的构图" |
| **Mask 修复** | 1 张 | 1 张(需Alpha通道) | "把遮罩区域替换成玻璃幕墙大楼" |

#### 重要限制

- gpt-image-2 官方: 最多 16 张参考图，每张 ≤10MB，Mask ≤50MB
- gpt-image-2 自动开启 high-fidelity，**禁止传入 `input_fidelity`** 参数
- gpt-image-2-all/vip: 不支持 mask 局部编辑，用自然语言改图代替
- FLUX: 最多 8 张参考图
- Seedream: 最多 10 张参考图

### 3.2 方式二: /v1/chat/completions (对话式编辑)

**支持模型**: gpt-image-2-all / gpt-image-2-vip / Nano Banana

**优势**: 支持多轮对话迭代、支持直接传图片 URL (免上传)

```python
import requests
import base64

# 把本地图片编码为 data URL
with open("photo.jpg", "rb") as f:
    data_url = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

resp = requests.post(
    "https://api.apiyi.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-image-2-all",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "把这张照片变成吉卜力动画风格"},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }]
    },
    timeout=300
).json()

# 响应格式是 {data: [{url}]}，不是标准 Chat 格式
print(resp["data"][0]["url"])
```

#### 多轮迭代编辑

```python
messages = [
    {"role": "user", "content": "画一只猫"},
]
resp1 = requests.post(url, json={"model": "gpt-image-2-all", "messages": messages})
cat_url = resp1.json()["data"][0]["url"]

# 第二轮: 在前一轮基础上修改
messages.append({"role": "assistant", "content": None})  # 占位
messages.append({"role": "user", "content": [
    {"type": "text", "text": "给这只猫加一顶巫师帽"},
    {"type": "image_url", "image_url": {"url": cat_url}}
]})
resp2 = requests.post(url, json={"model": "gpt-image-2-all", "messages": messages})
```

### 3.3 方式三: images.generate 传参考图 (Seedream 统一架构)

Seedream 模型在同一 `images.generate` 端点同时支持生图和编辑:

```python
# 文本生图
resp = client.images.generate(
    model="seedream-5-0-260128",
    prompt="一只柴犬在沙滩奔跑",
)

# 单图编辑 (同一端点!)
resp = client.images.generate(
    model="seedream-5-0-260128",
    prompt="给这只柴犬戴上墨镜",
    image=["https://example.com/dog.jpg"],  # 参考图 URL
)

# 多图融合
resp = client.images.generate(
    model="seedream-5-0-260128",
    prompt="融合 image 1 的狗和 image 2 的海滩背景",
    image=["url1", "url2"],
)

# 批量序列生成
resp = client.images.generate(
    model="seedream-5-0-260128",
    prompt="连环画: 一个小孩从种树到收获的4个阶段",
    extra_body={
        "sequential_image_generation": "auto",
        "max_images": 4,
    }
)
```

---

## 4. 文生视频 API (Text-to-Video)

API易 提供 **2 个视频生成模型**: Sora 2 (OpenAI) 和 Veo 3.1 (Google)。

### 4.1 Sora 2 (OpenAI)

#### 模型变体

| 模型 ID | 时长 | 分辨率 | 价格 |
|---------|------|--------|------|
| `sora_video2` | 4/8/12/15s | 720×1280 (竖屏) | $0.12/次 (反向) 或 $0.10/秒 (官转) |
| `sora_video2-landscape` | 4/8/12/15s | 1280×720 (横屏) | 同上 |
| `sora_video2-15s` | 15s | 720×1280 | $0.12/次 |
| `sora-2-pro` | 4/8/12s | 720p/1024p/1080p | $0.30~$0.70/秒 |

#### 同步流式调用 (Chat Completions 端点)

```python
import requests

resp = requests.post(
    "https://api.apiyi.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "sora_video2",
        "stream": True,
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "一只可爱的金毛犬在公园草地上追逐飞盘，阳光明媚，慢动作"
            }]
        }]
    },
    stream=True,
    timeout=600
)

for line in resp.iter_lines():
    if line:
        print(line.decode())
```

#### 异步提交 (推荐生产环境)

```python
# Step 1: 提交任务
resp = requests.post(
    "https://api.apiyi.com/v1/videos",
    headers={"Authorization": "Bearer sk-xxx"},
    data={
        "model": "sora-2",
        "prompt": "一只猫在屋顶散步，夕阳背景，电影质感",
        "seconds": "8",          # 必须是字符串 "4"/"8"/"12"
        "size": "1280x720",
    },
    timeout=30
)
video_id = resp.json()["id"]

# Step 2: 轮询状态 (建议每 30 秒)
import time
while True:
    status_resp = requests.get(
        f"https://api.apiyi.com/v1/videos/{video_id}",
        headers={"Authorization": "Bearer sk-xxx"}
    )
    status = status_resp.json()
    if status["status"] == "completed":
        break
    elif status["status"] == "failed":
        raise Exception("Video generation failed")
    time.sleep(30)

# Step 3: 下载视频
video_resp = requests.get(
    f"https://api.apiyi.com/v1/videos/{video_id}/content",
    headers={"Authorization": "Bearer sk-xxx"}
)
with open("output.mp4", "wb") as f:
    f.write(video_resp.content)
```

#### 关键参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | `sora_video2` / `sora-2` / `sora-2-pro` |
| `prompt` | string | 是 | 视频描述 |
| `seconds` | string | 是 | `"4"` / `"8"` / `"12"` — **必须是字符串** |
| `size` | string | 是 | `1280x720` 或 `720x1280` |
| `stream` | boolean | 否 | 同步模式开启流式输出 |

### 4.2 Veo 3.1 (Google DeepMind)

#### 模型变体

| 模型 ID | 说明 | 价格 |
|---------|------|------|
| `veo-3.1` | 默认竖屏 | $0.25/条 |
| `veo-3.1-fast` | 竖屏快速版 | **$0.15/条** |
| `veo-3.1-landscape` | 横屏 | $0.25/条 |
| `veo-3.1-landscape-fast` | 横屏快速版 | $0.15/条 |

所有模型后缀可组合 `-fl` (Frame-to-Video 图生视频模式)。

#### 同步流式调用

```python
resp = requests.post(
    "https://api.apiyi.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "veo-3.1-fast",
        "stream": True,
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "海浪拍打岩石，日落时分，慢动作，电影级画质"
            }]
        }]
    },
    stream=True,
    timeout=600
)
```

#### 关键特性

- 固定 **8 秒** 视频
- 原生 **同步音频** (环境音、对话、配乐)
- Fast 版 30-60s 出片，标准版 1-2 分钟
- `n` 参数支持 1-4 并行生成变体
- 4K 系列正在推出

---

## 5. 图生视频 API (Image-to-Video)

### 5.1 Sora 2 图生视频

通过 Chat Completions 端点传入参考图:

```python
import requests, base64

with open("reference.png", "rb") as f:
    data_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()

resp = requests.post(
    "https://api.apiyi.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "sora_video2",
        "stream": True,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "让这个场景动起来，添加微风和飘落的花瓣"},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }]
    },
    stream=True,
    timeout=600
)
```

> 参考图尺寸必须与 `size` 参数完全匹配，否则返回 400 错误。

异步模式:

```python
resp = requests.post(
    "https://api.apiyi.com/v1/videos",
    headers={"Authorization": "Bearer sk-xxx"},
    data={
        "model": "sora-2",
        "prompt": "让场景动起来",
        "seconds": "8",
        "size": "1280x720",
    },
    files={
        "input_reference": ("ref.png", open("ref.png", "rb"), "image/png"),
    },
    timeout=30
)
```

### 5.2 Veo 3.1 Frame-to-Video (-fl 模式)

Veo 3.1 支持两种图生视频模式:

**模式 1: 单帧参考 (1 张起始图)**

```python
resp = requests.post(
    "https://api.apiyi.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "veo-3.1-fast-fl",  # 加 -fl 后缀
        "stream": True,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "让这个画面自然运动"},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }]
    },
    stream=True,
    timeout=600
)
```

**模式 2: 首尾帧控制 (2 张图定义起点和终点)**

异步模式:

```python
resp = requests.post(
    "https://api.apiyi.com/v1/videos",
    headers={"Authorization": "Bearer sk-xxx"},
    data={
        "model": "veo-3.1-fl",
        "prompt": "平滑过渡从起始画面到结束画面",
        "size": "720x1280",
    },
    files={
        "image[0]": ("start.png", open("start.png", "rb"), "image/png"),
        "image[1]": ("end.png", open("end.png", "rb"), "image/png"),
    },
    timeout=30
)
```

这个模式可以精确控制视频的起点和终点，适合做产品变换动画、前后对比等。

#### Sora vs Veo 图生视频对比

| 特性 | Sora 2 | Veo 3.1 |
|------|--------|---------|
| 参考图模式 | 1 张，作为风格/角色参考 | 1 张 (起始帧) 或 2 张 (首尾帧) |
| 首尾帧精确控制 | 不支持 | **支持** |
| 视频时长 | 4/8/12/15s | 固定 8s |
| 参考图尺寸要求 | 必须与 size 严格匹配 | 同 |
| 价格 | $0.12/次起 | $0.15/次起 |

---

## 6. 图片模型完整对比

### 6.1 快速选型

| 需求 | 推荐模型 |
|------|----------|
| 最高质量 + 精细参数控制 | `gpt-image-2` (quality=high) |
| 最快速度 + 最便宜 + 中文好 | **`gpt-image-2-all`** ($0.03, 30-60s) |
| 固定尺寸 + 4K + $0.03 | `gpt-image-2-vip` (30 档尺寸) |
| 照片级真实感 + 快速 | `flux-2-pro` ($0.03, <10s) |
| 4K + 文字渲染突破 | `seedream-4-5` ($0.04) |
| 对话式编辑 + 多轮迭代 | `gpt-image-2-all` + Chat 端点 |
| 品牌色精确控制 + 长 prompt | `flux-2-max` (32K tokens) |
| 批量序列生成 (连环画) | `seedream-5-0` (最多 15 张) |
| 图片搜索参考 + 4K | `gemini-3.1-flash-image-preview` |

### 6.2 价格速查 (单张 1024x1024)

| 模型 | 最低价 | 最高价 |
|------|--------|--------|
| gpt-image-2-all | **$0.03** | $0.03 |
| gpt-image-2-vip | **$0.03** | $0.03 |
| sora-image | **$0.01** | $0.01 |
| flux-2-klein | **$0.01** | $0.01 |
| seedream-4-0 | **$0.03** | $0.03 |
| gpt-image-2 (official) | $0.006 | $0.211 |
| gpt-image-1-mini | 更低 | 更低 |
| nano-banana-2 | $0.025 | $0.07 |

### 6.3 能力矩阵

| 能力 | gpt-image-2 | gpt-image-2-all | gpt-image-2-vip | FLUX.2 | Seedream | NanoBanana2 |
|------|:-----------:|:---------------:|:---------------:|:------:|:--------:|:-----------:|
| size 参数 | 自定义 | 用 prompt | 30 档 | 自定义 | 预设 | 预设 |
| quality 参数 | 4 档 | 无 | 无 | 无 | 无 | 无 |
| 4K | 支持 | 不支持 | **支持** | 4MP | **4096** | **4096** |
| Mask 修复 | 支持 | 不支持 | 不支持 | 不支持 | 不支持 | 不支持 |
| 多图融合 | 16 张 | 16 张 | 16 张 | 8 张 | 10 张 | 14+4 张 |
| 对话式编辑 | 不支持 | **支持** | **支持** | 不支持 | 不支持 | **支持** |
| Web 搜索 | 不支持 | 不支持 | 不支持 | **max** | 不支持 | **支持** |
| URL 响应 | 不支持 | 支持 | 支持 | 支持 | 支持 | 支持 |
| Hex 颜色 | 不支持 | 不支持 | 不支持 | **支持** | 不支持 | 不支持 |
| 批量序列 | 不支持 | 不支持 | 不支持 | 不支持 | **15 张** | 不支持 |

---

## 7. 视频模型完整对比

### 7.1 Sora 2 vs Veo 3.1

| 维度 | Sora 2 (OpenAI) | Veo 3.1 (Google) |
|------|-----------------|-------------------|
| 时长 | 4/8/12/15s | 固定 8s |
| 分辨率 | 720p/1024p/1080p | 720p (4K 即将推出) |
| 音频 | 同步音频 | 同步音频 |
| 文生视频 | 支持 | 支持 |
| 图生视频 | 1 张参考图 | 1 张起始帧 / 2 张首尾帧 |
| 最低价格 | $0.12/次 (反向) / $0.10/秒 (官转) | **$0.15/次** (fast) |
| 最高价格 | $0.70/秒 (1080p Pro) | $0.25/次 (标准) |
| 生成时间 | 3-10 分钟 | fast 30-60s / 标准 1-2min |
| 并发生成 | 不支持 | n=1-4 并行 |
| 调用方式 | Chat + Async | Chat (流式) + Async |
| 视频存储 | 1 天 | 1 天 |

### 7.2 快速选型

| 需求 | 推荐模型 |
|------|----------|
| 最长视频 (15s) + 电影质感 | Sora 2 (反向 15s 版) |
| 最快 + 最便宜 | **Veo 3.1 Fast** ($0.15, 30-60s) |
| 首尾帧精确控制 | Veo 3.1 -fl (2 张图) |
| 风格参考创作 | Sora 2 (参考图模式) |
| 并行批量生成 | Veo 3.1 (`n=4`) |
| 1080p 专业级 | Sora 2 Pro (官转) |

---

## 8. 最佳实践

### 8.1 省钱策略

1. **日常测试用 cheap 模型**: `flux-2-klein` ($0.01) > `gpt-image-2-all` ($0.03) > `gpt-image-2` low ($0.006)
2. **官方 high 太贵?** 先用 `quality=low` 预览构图，确定后再用 `high` 出成品
3. **all vs vip**: 不需要精确控尺寸就用 all (更快)，需要 4K 用 vip
4. **4K 省钱**: 用 vip ($0.03 含 4K) 替代 official (4K token 计费更贵)
5. **视频先测试再量产**: 先用 Veo Fast ($0.15) 测试 prompt，确认后用 Sora 2 Pro 出成品

### 8.2 生图 Prompt 公式

```
[主体] + [场景/背景] + [风格/画风] + [光线/氛围] + [技术参数]

示例: "一只柴犬 (主体) 在秋叶飘落的公园里奔跑 (场景),
      吉卜力动画风格 (风格), 温暖的午后阳光 (光线), 4K高清 (参数)"
```

### 8.3 图片编辑 Prompt 指代

在使用 `/v1/images/edits` 多图融合时:

```
"融合图1的构图和风格，图2中的角色，图3的背景色调，
 添加中文字'秋日物语'作为标题"
```

### 8.4 视频生成注意事项

- `seconds` 参数**必须是字符串**: `"8"` 而非 `8`
- Sora 图生视频: 参考图尺寸必须与 `size` 严格匹配
- 视频 URL 有效期仅 1 天，生成后立即下载
- 推荐用**异步模式**提交视频任务，失败不扣费
- Veo `-fl` 模式: 首尾帧图分辨率要与目标视频一致

### 8.5 Base URL 选择

```
OpenAI SDK 兼容 → https://api.apiyi.com/v1 (主) 或 https://vip.apiyi.com/v1 (高性能)
纯文本 LLM      → https://api-cf.apiyi.com/v1 (CDN)
Gemini 原生格式  → https://api.apiyi.com (不加 /v1)
```

### 8.6 错误处理

```python
try:
    resp = client.images.generate(...)
except openai.BadRequestError as e:
    # 400: 参数错误，检查 size/quality 是否被该模型支持
    print(f"参数错误: {e}")
except openai.RateLimitError:
    # 429: 限流，等待重试
    time.sleep(5)
except openai.APITimeoutError:
    # 超时: 高画质可能需要 200s+，设置足够的 timeout
    print("生成超时，考虑降低 quality 或换更快模型")
```

### 8.7 模型选择决策树

```
需要生成图片?
├─ 需要精细控制 (quality/size/mask)?
│  └─ gpt-image-2 (official, token 计费)
├─ 最快最便宜 + 中文好?
│  └─ gpt-image-2-all ($0.03, 30-60s)
├─ 需要 4K + 固定尺寸 + $0.03?
│  └─ gpt-image-2-vip (30 档尺寸)
├─ 照片级真实 + 品牌色?
│  └─ flux-2-pro ($0.03, <10s)
├─ 需要编辑/对话/多轮?
│  └─ gpt-image-2-all + /v1/chat/completions
└─ 批量序列/连环画?
   └─ seedream-5-0 (最多 15 张)

需要生成视频?
├─ 首尾帧精确控制?
│  └─ Veo 3.1 -fl (2 图)
├─ 最长 15s + 电影感?
│  └─ Sora 2 反向 15s
├─ 最快 + 最便宜?
│  └─ Veo 3.1 Fast ($0.15, 30-60s)
└─ 1080p 专业级?
   └─ Sora 2 Pro 官转
```

---

## 附录: 本地项目快速参考

本项目 (`E:\AI\Test\Test_ImageV2`) 已封装好以下能力:

```python
from src.client import generate_image, generate_multiple, edit_image, chat_generate
from src.utils import save_images

# 基础生图
result = generate_image(prompt="...", model="gpt-image-2", quality="low")
save_images([result], prefix="test")

# 多图
results = generate_multiple(prompt="...", count=4, model="gpt-image-2-all")

# 图片编辑
result = edit_image(prompt="...", image_paths=["ref.png"], model="gpt-image-2")
```

运行示例:
```bash
python examples/01_basic_generate.py   # 基础
python examples/02_multi_image.py      # 模型对比
python examples/05_chinese_text.py     # 中文渲染
python examples/08_quality_comparison.py # 画质对比
python examples/09_image_editing.py    # 图片编辑
```

> 更多细节见各示例文件的注释。
