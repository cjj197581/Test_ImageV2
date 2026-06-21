# gpt-image-2 (ChatGPT Images 2.0) 文本转图片学习项目 —— 完整总结报告

> 整理日期: 2026-05-27
> 中转服务: API易 (apiyi.com)
> 模型: gpt-image-2 / gpt-image-2-all / gpt-image-2-vip

---

## 目录

1. [项目概述](#1-项目概述)
2. [项目架构](#2-项目架构)
3. [核心模块详解](#3-核心模块详解)
4. [9 个示例脚本](#4-9-个示例脚本)
5. [实践中的关键发现](#5-实践中的关键发现)
6. [遇到的错误及解决方案](#6-遇到的错误及解决方案)
7. [生成的图片展示](#7-生成的图片展示)
8. [API易 三模型对比](#8-api易-三模型对比)
9. [最佳实践总结](#9-最佳实践总结)
10. [项目文件清单](#10-项目文件清单)

---

## 1. 项目概述

### 背景

OpenAI 于 2026年4月22日 发布了 **gpt-image-2**（ChatGPT Images 2.0），相比上一代在以下方面有显著提升：

- 中文/日文/韩文文字精准渲染（99% 准确率）
- 支持 3:1 到 1:3 的任意宽高比
- 最高 4K 分辨率输出
- 支持 seed 种子控制保持风格一致
- 支持 quality 参数（low/medium/high/auto）按需调节质量与速度

由于 OpenAI 对 API Key 申请要求严苛（需海外手机号/信用卡），本项目的 API 调用通过国内中转服务 **API易 (apiyi.com)** 实现。

### 目标

- 学习 gpt-image-2 模型的各项能力
- 封装可复用的 Python 客户端库
- 编写递进式示例脚本覆盖从基础到高级的全部功能
- 全面了解 API易 平台的图片/视频生成 API
- 整理完整的使用指南和最佳实践

---

## 2. 项目架构

```
E:\AI\Test\Test_ImageV2\
├── .env                          # API Key 配置 (gitignore)
├── .env.example                  # 配置模板
├── .gitignore
├── requirements.txt              # Python 依赖
├── APIYI_完整使用指南.md          # API易 全部功能使用指南 (~850行)
├── PROJECT_SUMMARY.md            # 本报告
│
├── src/                          # 核心库
│   ├── __init__.py
│   ├── config.py                 # 配置加载 + 模型能力矩阵
│   ├── client.py                 # API 客户端 (4个端点 + 重试)
│   └── utils.py                  # 工具函数 (解码/保存/下载)
│
├── examples/                     # 9 个递进式示例
│   ├── 01_basic_generate.py      # 基础文生图
│   ├── 02_multi_image.py         # 多图 + 三模型对比
│   ├── 03_seed_control.py        # 种子控制
│   ├── 04_aspect_ratios.py       # 宽高比 + 2K
│   ├── 05_chinese_text.py        # 中文文字渲染
│   ├── 06_streaming.py           # 流式 (带降级)
│   ├── 07_webhook.py             # WebHook (带降级)
│   ├── 08_quality_comparison.py  # low/medium/high 画质对比
│   └── 09_image_editing.py       # 图片编辑 (参考图→改图)
│
├── output/                       # 生成的图片 (10+ 张)
│   ├── cat_*.png                 # 基础生图测试
│   ├── cn_poster_*.png           # 中文海报测试
│   ├── cn_label_*.png            # 中文标签测试
│   ├── cn_app_*.png              # 中文启动页测试
│   ├── multi_test_*.png          # 多图生成测试
│   ├── api_test_*.png            # 官方模型测试
│   ├── vip_test_*.png            # VIP 模型测试
│   ├── fallback_cat_*.png        # 流式降级测试
│   └── webhook_fallback_*.png    # WebHook 降级测试
│
└── memory/                       # 持久化记忆 (Claude Code)
```

### 依赖

```
openai>=1.55.0      # OpenAI Python SDK (兼容中转服务)
python-dotenv        # 从 .env 加载环境变量
requests             # HTTP 请求 (multipart 编辑 / 流式)
Pillow               # 图片查看
```

---

## 3. 核心模块详解

### 3.1 config.py —— 配置中心

包含三大职责：

**A. 环境变量加载**

```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.chatanywhere.com.cn")
```

**B. 模型能力矩阵 MODEL_CAPABILITIES**

这是整个项目的核心数据结构。每个模型的能力差异极大，通过字典驱动代码行为而非硬编码 if/else：

```python
MODEL_CAPABILITIES = {
    MODEL_OFFICIAL: {
        "quality": True,          # 支持 low/medium/high/auto
        "size_param": True,       # 支持自定义尺寸
        "4k": True,               # 实验性 4K
        "mask_inpainting": True,  # 支持 Mask 局部重绘
        "chat_completions": False,# 不支持对话端点
        "response_url": False,    # 仅返回 b64_json (纯 base64)
        "b64_prefix": "",         # 无 data: 前缀
        "pricing": "token 计费, $0.006~$0.211/张",
        "speed": "low 3-8s / medium 25-40s / high 200-240s",
        "n_limit": 1,
        "default_size": "auto",
    },
    MODEL_ALL: { /* ... */ },
    MODEL_VIP: { /* ... */ },
}
```

**C. 常量定义**

- 3 个模型常量: `MODEL_OFFICIAL`, `MODEL_ALL`, `MODEL_VIP`
- 4 个画质常量: `QUALITY_LOW`, `QUALITY_MEDIUM`, `QUALITY_HIGH`, `QUALITY_AUTO`
- 30 档 VIP 尺寸 (10 比例 × 3 分辨率)
- 3 种输出格式 + 2 种响应格式

### 3.2 client.py —— API 客户端

封装了 API易 的全部 4 个端点：

| 函数 | 端点 | 支持的模型 |
|------|------|-----------|
| `generate_image()` | `/v1/images/generations` | 所有模型 |
| `edit_image()` | `/v1/images/edits` | gpt-image-2 / FLUX / Seedream |
| `chat_generate()` | `/v1/chat/completions` | all / vip / Gemini |
| `draw_completion()` | `/draw/completions` | (API易不支持) |

**核心设计 —— 智能参数适配：**

`generate_image()` 通过 `_cap(model)` 查询能力矩阵来决定参数行为：

```python
caps = _cap(model)

# 智能默认值: 官方/VIP 默认 auto, all 不传 size
if size is None:
    size = caps.get("default_size") or SIZE_AUTO

# quality 仅官方模型支持
if quality is None and caps.get("quality"):
    quality = QUALITY_AUTO

# gpt-image-2-all 不支持 size 参数，跳过
if caps.get("size_param", True):
    params["size"] = size

# 自定义参数必须通过 extra_body 传递
extra_body = {}
if seed is not None:
    extra_body["seed"] = seed
if quality:
    extra_body["quality"] = quality
```

**带重试封装：**

```python
def generate_with_retry(prompt, max_retries=3, delay=2.0, **kwargs):
    for attempt in range(max_retries):
        try:
            return generate_image(prompt=prompt, **kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # 指数退避
    raise last_err
```

### 3.3 utils.py —— 工具函数

**base64 兼容解码** —— 这是解决 API易 格式不一致问题的关键：

```python
def decode_b64(data: str) -> tuple[bytes, str]:
    if data.startswith("data:"):
        # 官逆模型: "data:image/png;base64,iVBORw0..."
        header, b64 = data.split(",", 1)
        m = re.search(r"image/(\w+)", header)
        if m:
            ext = m.group(1)
        return base64.b64decode(b64), ext
    else:
        # 官方模型: 纯 base64 "iVBORw0KGgo..."
        return base64.b64decode(data), "png"
```

**批量保存：**

```python
def save_images(results, prefix="image"):
    timestamp = int(time.time())
    for i, result in enumerate(results):
        img_bytes, ext = decode_b64(result["b64_json"])
        model_tag = result["model"].rsplit("/", 1)[-1]
        filepath = OUTPUT_DIR / f"{prefix}_{model_tag}_{timestamp}_{i}.{ext}"
        filepath.write_bytes(img_bytes)
```

---

## 4. 9 个示例脚本

### 01 — 基础文生图 (`01_basic_generate.py`)

最简调用：输入文字 → 输出图片。使用官方模型默认 quality=auto，约 30-60 秒完成。

```python
result = generate_image(
    prompt="一只可爱的橙色虎斑猫坐在窗台上，阳光从窗外照进来，温暖的午后氛围",
    size="1024x1024",
)
save_images([result], prefix="cat")
```

> 生成图片: `output/cat_1779882309_0.png`

### 02 — 多图生成 + 三模型对比 (`02_multi_image.py`)

对比 gpt-image-2 (官方)、gpt-image-2-all ($0.03/张)、gpt-image-2-vip ($0.03/张, 4K) 三个模型的生成效果。是关键的成本/质量选型参考。

```python
# 官方模型 - token 计费，支持 size
results = generate_multiple(prompt=prompt, count=2, model=MODEL_OFFICIAL, size="1024x1024")

# all 模型 - $0.03 统一价，不支持 size 参数
all_results = generate_multiple(prompt=prompt, count=2, model=MODEL_ALL)

# vip 模型 - $0.03 统一价，支持 30 档尺寸含 4K
vip_result = generate_image(prompt=prompt, model=MODEL_VIP, size="1792x1024")
```

> 生成图片: `output/multi_test_*.png`, `output/corgi_*.png`

### 03 — 种子控制 (`03_seed_control.py`)

固定 seed=42，仅改变 prompt 中的主体（黑猫→白猫→橘猫），测试风格一致性。

```python
seed = 42
for prompt in ["黑猫坐在沙发上", "白猫坐在沙发上", "橘猫坐在沙发上"]:
    result = generate_image(prompt=prompt, size="1024x1024", seed=seed)
```

### 04 — 宽高比 (`04_aspect_ratios.py`)

测试 16:9 (宽屏)、1:1 (正方形)、9:16 (竖屏) 三种常用比例。

```python
test_sizes = {
    "1792x1024": "宽屏 16:9 —— 视频封面",
    "1024x1024": "正方形 1:1 —— Instagram",
    "1024x1792": "竖屏 9:16 —— 手机壁纸",
}
```

### 05 — 中文文字渲染 (`05_chinese_text.py`)

测试 gpt-image-2 的中文文字渲染能力，包含三种场景：
- 海报: "春日花语"
- 产品标签: "纯天然蜂蜜 / 净含量 500g / 产地 云南"
- App 启动页: "每日阅读 / 每天进步一点点"

```python
result = generate_image(
    prompt="一张现代简约风格的海报，中央用漂亮的中文艺术字体写着'春日花语'...",
    size="1024x1024",
    quality=QUALITY_HIGH,  # 文字密集型推荐高画质
)
```

> 生成图片: `output/cn_poster_*.png`, `output/cn_label_*.png`, `output/cn_app_*.png`

### 06 — 流式响应 (`06_streaming.py`)

尝试 `/draw/completions` 流式端点。API易 不支持此端点时自动降级为标准 `generate_image()`。

```python
try:
    for event in draw_completion_stream(prompt="...", size="1024x1024"):
        print(f"[事件] {event.get('type')}")
except Exception as e:
    if any(k in str(e) for k in ("404", "not found", "html", "不支持")):
        # 自动降级
        result = generate_image(prompt="...", size="1024x1024")
        save_images([result], prefix="fallback_cat")
```

> 降级生成图片: `output/fallback_cat_*.png`

### 07 — WebHook 异步 (`07_webhook.py`)

与 06 类似，尝试异步提交后自动降级。

> 降级生成图片: `output/webhook_fallback_*.png`

### 08 — 画质对比 (`08_quality_comparison.py`)

用同一 prompt 分别测试 low、medium、high 三种画质，记录耗时。

```python
for quality in [QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH]:
    start = time.time()
    result = generate_image(prompt=prompt, size="1024x1024", quality=quality)
    elapsed = time.time() - start
    print(f"画质: {quality} | 耗时: {elapsed:.0f}s")
```

预期耗时: low 3-8s / medium 25-40s / high 200-240s

### 09 — 图片编辑 (`09_image_editing.py`)

先 `generate_image()` 生成一张参考图（名片模板），再通过 `edit_image()` 在参考图上添加中文文字。

```python
# Step 1: 生成参考图
ref_result = generate_image(
    prompt="一张空白的现代简约风格名片模板...",
    quality="low",
)

# Step 2: 基于参考图编辑
edit_result = edit_image(
    prompt="在这张名片模板上添加公司名称'星辰科技'和职位'产品经理'...",
    image_paths=[str(reference_path)],
    model=MODEL_OFFICIAL,
    size="1024x1024",
)
```

---

## 5. 实践中的关键发现

### 5.1 gpt-image-2 n=1 限制

所有 gpt-image-2 系列模型 **n 固定为 1**，不能像旧版 DALL-E 那样单次请求生成多张图片。多图场景需要循环调用 `generate_image()`。项目通过 `generate_multiple()` 封装了这一逻辑。

### 5.2 三个模型的三条技术路线

这是本项目最重要的发现 —— API易 的 gpt-image-2 实际上有三条不同的技术路线：

```
gpt-image-2 (官方)
  └─ OpenAI 官方 API 转发
     ├─ Token 计费，精细控制 quality/size
     └─ 返回纯 base64 (无 data: 前缀)

gpt-image-2-all (官逆 ChatGPT Web 线)
  └─ 逆向 ChatGPT Web 端 API
     ├─ $0.03/张 统一价，30-60s
     ├─ 不支持 size 参数（尺寸通过 prompt 描述）
     └─ 文档说 b64 带 data: 前缀

gpt-image-2-vip (官逆 Codex 线)
  └─ 逆向 Codex 端 API
     ├─ $0.03/张 统一价 (含4K)，90-150s
     ├─ 支持 30 档固定尺寸
     └─ 支持 url 响应格式和 chat/completions 端点
```

### 5.3 base64 格式不一致

API易 不同模型返回的 base64 格式不同：
- **官方模型**: 纯 base64 `iVBORw0KGgo...`
- **官逆模型 (all/vip)**: 文档说带 `data:image/png;base64,` 前缀，实测中 vip 也返回纯 base64

`decode_b64()` 通过检测 `data:` 前缀来兼容所有情况。

### 5.4 参数分两路传递

OpenAI Python SDK 的 `images.generate()` 签名固定，不支持 gpt-image-2 的扩展参数。项目发现必须将自定义参数分为两路：

| 传递方式 | 参数 |
|---------|------|
| 直接参数 | `model`, `prompt`, `size`, `n` |
| `extra_body` | `seed`, `quality`, `output_format`, `output_compression`, `background`, `moderation` |

### 5.5 /draw/completions 端点不可用

API易 目前不支持 `/draw/completions` 端点（返回 HTML 或 404）。示例 06 和 07 实现了自动降级到标准 `generate_image()` 的逻辑。如需流式/WebHook 功能，可考虑备选服务诗云API (shuyunapi.com)。

### 5.6 中文错误消息检测

API易 返回的错误消息是中英文混合的。错误降级逻辑必须同时检测中文关键词（如 "不支持"、"未开放"）和英文关键词，否则降级逻辑会失效。

---

## 6. 遇到的错误及解决方案

### 错误 1: TypeError — seed 参数不识别

```
TypeError: Images.generate() got an unexpected keyword argument 'seed'
```

**原因**: OpenAI SDK 的 `images.generate()` 不认识 seed 参数（非标准 DALL-E API 的一部分）。

**解决**: 将 seed 以及所有 gpt-image-2 扩展参数移入 `extra_body` 字典。

**影响范围**: seed, quality, output_format, output_compression, background, moderation — 全部不受影响。

### 错误 2: ValueError — 无法识别 URL 类型

```
ValueError: unknown url type: 'iVBORw0KGgo...'
```

**原因**: API易 的官方模型返回纯 base64 数据（无 `data:` 前缀），而 `urlretrieve()` 无法识别纯 base64 字符串。

**解决**: 在 `download_image()` 和 `decode_b64()` 中添加纯 base64 检测分支。

### 错误 3: BadRequestError — Unknown parameter: 'size'

```
openai.BadRequestError: Unknown parameter: 'size'
```

**原因**: gpt-image-2-all 模型不支持 size 参数。

**解决**: 通过 `MODEL_CAPABILITIES[model]["size_param"]` 判断是否传入 size 参数。all 模型设 `size_param: False`。

### 错误 4: 404 — /v1/v1/draw/completions

```
HTTP 404: /v1/v1/draw/completions
```

**原因**: `BASE_URL` 已包含 `/v1`，直接拼接 `/v1/draw/completions` 产生双重 `/v1/v1/` 前缀。

**解决**: 计算 `_ROOT_URL = re.sub(r"/v\d+$", "", BASE_URL)`，从根路径构建 `/draw/completions` URL。

### 错误 5: response_format 参数不识别

```
openai.BadRequestError: Unknown parameter: 'response_format'
```

**原因**: API易 不支持 `response_format` 参数切换 url/b64_json，默认返回 b64_json。

**解决**: 移除 `response_format` 参数，`generate_image()` 始终接收 b64_json 响应。

### 错误 6: 流式/WebHook 降级未触发

**原因**: API易 返回的中文错误消息 "不支持此端点" 未被仅含英文关键词的错误检测逻辑捕获。

**解决**: 在降级检测逻辑中添加中文关键词 `"不支持"`, `"未开放"`, `"draw/completions"`。

---

## 7. 生成的图片展示

项目在开发测试过程中共生成 **10 张验证图片**，均保存在 `output/` 目录：

| 文件名 | 用途 | 模型 | 参数 |
|--------|------|------|------|
| `cat_1779882309_0.png` | 基础生图测试 | gpt-image-2 | quality=auto, 1024x1024 |
| `cn_poster_1779882482_0.png` | 中文海报 "春日花语" | gpt-image-2 | quality=high, 1024x1024 |
| `cn_label_1779882632_0.png` | 中文产品标签 | gpt-image-2 | quality=high, 1024x1024 |
| `cn_app_1779882784_0.png` | 中文 App 启动页 | gpt-image-2 | quality=high, 1024x1024 |
| `multi_test_1779883073_0.png` | 多图测试 (1/2) | gpt-image-2 | auto, 1024x1024 |
| `multi_test_1779883073_1.png` | 多图测试 (2/2) | gpt-image-2 | auto, 1024x1024 |
| `fallback_cat_1779883280_0.png` | 流式降级测试 | gpt-image-2 | auto, 1024x1024 |
| `webhook_fallback_1779883414_0.png` | WebHook 降级测试 | gpt-image-2 | auto, 1024x1024 |
| `api_test_gpt-image-2_1779883807_0.png` | 官方模型专项 | gpt-image-2 | auto, 1024x1024 |
| `vip_test_gpt-image-2-vip_1779884290_0.png` | VIP 模型专项 | gpt-image-2-vip | auto, 1024x1024 |

**图片特征**: 全部为 1024x1024 PNG RGB 格式，文件大小约 1-2.3MB。

---

## 8. API易 三模型对比

| 维度 | gpt-image-2 (官方) | gpt-image-2-all | gpt-image-2-vip |
|------|:---:|:---:|:---:|
| 最低价格 | $0.006 (low) | **$0.03** | **$0.03** |
| 最高价格 | $0.211 (high) | $0.03 | $0.03 |
| 最快速度 | **3-8s** (low) | 30-60s | 90-150s |
| 最慢速度 | 200-240s (high) | — | — |
| quality 参数 | low/medium/high/auto | 不支持 | 不支持 |
| size 自定义 | 16倍数, ≤3840px | prompt 描述 | 30 档预设 |
| 4K 输出 | 实验性 | 不支持 | **正式支持** |
| Mask 修复 | 支持 | 不支持 | 不支持 |
| 对话式编辑 | 不支持 | 支持 | 支持 |
| URL 响应 | 不支持 | 支持 | 支持 |

### 选型建议

```
日常测试/便宜  → gpt-image-2-all ($0.03, 30-60s)
              → gpt-image-2 quality=low ($0.006, 3-8s)

正式出图/质量  → gpt-image-2 quality=high ($0.211, 200s)
              → gpt-image-2 quality=medium ($0.053, 30s)

4K 输出       → gpt-image-2-vip ($0.03, 含 4K)

对话式编辑    → gpt-image-2-all + /v1/chat/completions

Mask 局部重绘 → gpt-image-2 官方 (仅此模型支持)
```

---

## 9. 最佳实践总结

### 9.1 省钱策略

1. **日常测试**: 先用 `quality=low` ($0.006) 验证 prompt 效果，确认后用 `high` 出成品
2. **4K 省钱**: 用 vip ($0.03 含 4K) 代替 official (4K 时 token 计费远高于 $0.03)
3. **all vs vip**: 不需要精确控尺寸用 all (更快)，需要 4K 用 vip
4. **中转服务**: 不要大额充值，用多少充多少，先小金额测试

### 9.2 代码规范

1. **参数透传**: 扩展参数一律走 `extra_body`，不走直接参数
2. **能力查询**: 通过 `MODEL_CAPABILITIES` 字典驱动参数行为，不硬编码 if/else
3. **错误检测多语言**: 同时检测中文和英文错误关键词
4. **降级优先**: 对不保证可用的端点（如 /draw/completions）实现自动降级
5. **base64 兼容**: 始终兼容带/不带 `data:` 前缀的两种格式

### 9.3 Prompt 公式

```
[主体] + [场景/背景] + [风格/画风] + [光线/氛围] + [技术参数]

示例:
"一只柴犬 (主体) 在秋叶飘落的公园里奔跑 (场景),
 吉卜力动画风格 (风格), 温暖的午后阳光 (光线), 4K高清 (参数)"
```

### 9.4 安全提醒

- `.env` 文件已在 `.gitignore` 中排除，防止 API Key 泄露
- API Key 如已公开或怀疑泄露，请在 apiyi.com 后台立即重置
- 不要在代码或配置文件中硬编码 API Key

---

## 10. 项目文件清单

### 核心模块 (3 文件, ~400 行)

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/config.py` | 158 | 配置加载、模型能力矩阵、常量定义 |
| `src/client.py` | 443 | API 客户端 (4端点 + 重试) |
| `src/utils.py` | 98 | 解码、保存、下载 |

### 示例脚本 (9 文件)

| 文件 | 功能 | 关键参数/模型 |
|------|------|--------------|
| `01_basic_generate.py` | 基础文生图 | quality=auto |
| `02_multi_image.py` | 多图 + 三模型对比 | official vs all vs vip |
| `03_seed_control.py` | 种子控制 | seed=42 |
| `04_aspect_ratios.py` | 宽高比 | 16:9 / 1:1 / 9:16 |
| `05_chinese_text.py` | 中文文字渲染 | quality=high |
| `06_streaming.py` | 流式(带降级) | /draw/completions |
| `07_webhook.py` | WebHook(带降级) | /draw/completions |
| `08_quality_comparison.py` | 画质对比 | low/med/high |
| `09_image_editing.py` | 图片编辑 | /images/edits |

### 文档

| 文件 | 说明 |
|------|------|
| `APIYI_完整使用指南.md` | ~850 行完整指南，覆盖全部图/视频 API |
| `PROJECT_SUMMARY.md` | 本报告 |

### Memory (9 个记忆文件)

| 记忆 | 类型 |
|------|------|
| `user_role.md` | 用户角色与背景 |
| `feedback_extra_body.md` | 扩展参数必须走 extra_body |
| `feedback_b64_format.md` | base64 格式兼容 |
| `feedback_size_param.md` | all 模型不支持 size |
| `feedback_fallback_detection.md` | 中文错误检测 |
| `feedback_url_construction.md` | URL 拼接 /v1 重复 |
| `feedback_input_fidelity.md` | 禁止传入 input_fidelity |
| `project_apiyi_models.md` | 三模型能力对比 |
| `reference_api_docs.md` | 外部文档索引 |

---

## 附录: 快速上手

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 填入 API_KEY 和 BASE_URL

# 3. 运行示例
python examples/01_basic_generate.py      # 基础: 1 张图
python examples/02_multi_image.py         # 对比: 3 模型 × 2 张
python examples/05_chinese_text.py        # 中文: 海报/标签/App页
python examples/08_quality_comparison.py  # 对比: low/medium/high
python examples/09_image_editing.py       # 编辑: 参考图→改图

# 4. 查看结果
ls output/
```

```python
# 在代码中使用
from src.client import generate_image, generate_multiple
from src.utils import save_images

result = generate_image(
    prompt="你的描述",
    model="gpt-image-2",     # 或 gpt-image-2-all / gpt-image-2-vip
    size="1024x1024",
    quality="auto",
)
save_images([result], prefix="my_image")
```
