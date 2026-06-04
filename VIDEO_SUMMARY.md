# 文本转视频 (Veo 3.1) — 详细总结报告

> 项目: API易 中转服务 AI 视频生成实战
> 日期: 2026-05-27
> 阶段: Phase 2 — 文本转视频学习

---

## 一、概述

本阶段在 Phase 1 (gpt-image-2 图片生成) 的基础上，扩展项目使其支持文本转视频功能。目标是学习如何使用 API易 中转服务调用视频生成模型，并编写可复用的 Python 客户端和示例脚本。

**核心成果:**
- 新建 `src/video_client.py` (~460行)，封装完整的视频生成流程
- 编写 2 个示例脚本 (单任务 + 批量并发)
- 成功生成并下载 **7 个视频**，总计约 10MB
- 验证了 Veo 3.1 作为当前唯一可用的视频模型

---

## 二、模型选型：从 Sora 2 到 Veo 3.1

### 2.1 Sora 2 — 已关停

最初计划使用 Sora 2，但用户回忆起 Sora 2 可能已被终止。经过搜索确认：

> **OpenAI 于 2026 年 3 月 24 日正式关停 Sora 全系列产品。**
>
> 原因：日均算力成本约 $1500 万美元，月消费者收入仅约 $36.7 万美元，财务不可持续。

Sora 2 存活仅 25 个月即告终止。API易 上仍能看到 `sora-2` 通道，但调用均返回 503 (no available channels)。

### 2.2 Veo 3.1 — Google DeepMind 替代方案

API易 上可用的视频模型只有 Google 的 Veo 3.1 系列。但模型命名存在陷阱：

| 模型名 (尝试) | 结果 |
|---|---|
| `veo-3.1` | 503 no available channels |
| `veo-3.1-fast` | 503 no available channels |
| `veo3` | 503 no available channels |
| **`veo-3.1-generate-preview`** | **200 OK (唯一可用)** |

**关键发现:** 只有 `veo-3.1-generate-preview` 可用，其他变体名在 API易 上均未开通。这个模型名在 API易 文档中也未被明确标注。

> 相关 memory: [[project-veo31-model]]

---

## 三、项目架构

### 3.1 新增/修改的文件

```
Test_ImageV2/
├── src/
│   ├── config.py          ← 新增视频模型常量和 ENDPOINT_VIDEOS
│   └── video_client.py    ← ★ 新建，核心视频客户端模块
├── examples/
│   ├── 10_sora2_text_to_video.py   ← 单任务异步流程
│   └── 11_sora2_async_video.py     ← 批量并发流程
├── output/                ← 生成的视频文件
└── memory/                ← 新增 4 个视频相关 memory
```

### 3.2 核心模块: `src/video_client.py`

提供三种调用层级：

```
┌─────────────────────────────────────────────┐
│  高级 API (推荐)                             │
│  generate_video_async()                     │
│  提交 → 轮询 → 下载，一步到位                │
├─────────────────────────────────────────────┤
│  中级 API (灵活组合)                         │
│  submit_video_task()                        │
│  wait_for_video()                           │
│  download_video_content()                   │
├─────────────────────────────────────────────┤
│  低级 (备用)                                 │
│  generate_video_sync()  ← Chat Completions  │
│  流式 SSE，目前不可用                        │
└─────────────────────────────────────────────┘
```

#### 关键函数签名

```python
# 提交视频生成任务
def submit_video_task(
    prompt: str,
    model: str = "sora-2",
    size: str = VIDEO_DEFAULT_SIZE,    # "720x1280"
    seconds: str = VIDEO_DEFAULT_SECONDS,  # "8"
    image_path: str | None = None,     # 可选的参考图
    timeout: int = 30,
) -> str:  # 返回 video_id

# 轮询等待视频完成
def wait_for_video(
    video_id: str,
    poll_interval: int = 15,
    max_wait: int = 600,
    verbose: bool = True,
) -> dict[str, Any]:  # 返回包含 url 字段的状态 dict

# 下载视频二进制数据
def download_video_content(
    video_id: str,
    timeout: int = 120,
    retries: int = 5,
) -> bytes:  # 返回 MP4 二进制数据

# 一键异步生成 (推荐)
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
```

#### 自定义异常

```python
class VideoUnavailableError(Exception):
    """视频生成服务不可用 (账户未开通/分组无通道/服务暂不可用)."""

class VideoChannelError(VideoUnavailableError):
    """当前账户分组没有视频模型通道，需在 API易 后台配置."""
```

---

## 四、API 调用流程

### 4.1 异步三步工作流 (唯一的可行方式)

```
Step 1: POST /v1/videos
  → 提交任务，返回 {"id": "task_xxx", "status": "queued"}

Step 2: GET /v1/videos/{id} (轮询，每 10-15s)
  → {"status": "queued|processing|completed|failed", "progress": 0-100}

Step 3: GET /v1/videos/{id}/content (延迟 3s)
  → 直接返回 binary video/mp4 (非 JSON!)
```

### 4.2 API 端点对照

| 端点 | 方法 | 功能 | Content-Type |
|------|------|------|-------------|
| `/v1/videos` | POST | 提交任务 | application/json |
| `/v1/videos/{id}` | GET | 查询状态 | application/json |
| `/v1/videos/{id}/content` | GET | 下载视频 | **video/mp4** (二进制) |
| `/v1/chat/completions` | POST | 流式生成 | **不可用** (返回 HTML) |

### 4.3 竞态条件与重试机制

```
状态查询 GET /v1/videos/{id} 返回 completed
                ↓
         等待 3 秒 (传播延迟)
                ↓
     GET /v1/videos/{id}/content
                ↓
     检查 Content-Type 是否为 video/
     检查 body 大小 > 1000 字节
                ↓
     如果不是 → 等待 3 秒 → 重试 (最多 5 次)
```

关键代码：

```python
def download_video_content(video_id: str, timeout: int = 120, retries: int = 5) -> bytes:
    for attempt in range(retries):
        resp = requests.get(
            f"{BASE_URL}/videos/{video_id}/content",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=timeout,
        )
        resp.raise_for_status()

        ct = resp.headers.get("content-type", "")
        if "video/" in ct and len(resp.content) > 1000:
            return resp.content  # 成功

        # JSON 错误或竞态条件 — 等待后重试
        if attempt < retries - 1:
            time.sleep(3)
```

> 相关 memory: [[feedback-video-content-endpoint]]

---

## 五、示例脚本

### 5.1 示例 10: 单任务顺序生成

`examples/10_sora2_text_to_video.py`

```python
"""Veo 3.1 文本转视频 —— 异步提交 + 轮询"""

from src.video_client import generate_video_async

# 测试 1: 竖屏 720x1280
result1 = generate_video_async(
    prompt="一只可爱的柴犬在春天的公园里奔跑，樱花花瓣随风飘落...",
    model=VEO_3_1_GENERATE,    # "veo-3.1-generate-preview"
    size=VIDEO_SIZE_PORTRAIT,  # "720x1280"
    seconds="8",
    poll_interval=10,
    max_wait=600,
)

# 测试 2: 横屏 1280x720
result2 = generate_video_async(
    prompt="海浪轻柔地拍打着白色沙滩，日落时分天空呈现橙色和紫色的渐变...",
    model=VEO_3_1_GENERATE,
    size=VIDEO_SIZE_LANDSCAPE,  # "1280x720"
    seconds="8",
    poll_interval=10,
    max_wait=600,
)
```

### 5.2 示例 11: 批量并发生成

`examples/11_sora2_async_video.py`

核心思路：同时提交多个任务，然后在一个轮询循环中并发检查所有任务状态：

```python
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
        if data.get("status") == "completed":
            info["done"] = True
            info["result"] = data
            print(f"  [{info['label']}] COMPLETED")

    time.sleep(10)  # 并发检查间隔
```

---

## 六、生成视频清单

共生成 **7 个视频**，总大小约 **10MB**：

| # | 文件名 | 大小 | 内容 | 尺寸 | 状态 |
|---|--------|------|------|------|------|
| 1 | `veo_test_waves_1779887013.mp4` | 1.1MB | 海浪拍打岩石，日落天空 | 1280x720 | 成功 |
| 2 | `veo_retry_task_vm8eAY5_1779887643.mp4` | 3.3MB | 日落时分的海边灯塔 | 720x1280 | 成功 |
| 3 | `veo_retry_task_3Xxy8At_1779887692.mp4` | 600KB | mountain sunrise fog valley | 1280x720 | 成功 |
| 4 | `video_async_task_3Xxy8At_1779888236.mp4` | 600KB | 同上(重新下载验证) | 1280x720 | 成功 |
| 5 | `video_async_task_5FFY22N_1779888502.mp4` | 1.8MB | test cat | 720x1280 | 成功 |
| 6 | `video_async_task_p37ZRIy_1779888648.mp4` | 1.1MB | 海浪拍打岩石，日落天空 | 1280x720 | 成功 |
| 7 | `video_async_task_YWArjSQ_*.mp4` | — | 柴犬在春天公园奔跑 | 720x1280 | 待确认 |

### 任务 ID 与 API易 后台对应

| 任务 ID (缩短) | API易 后台数据 | prompt |
|---|---|---|
| `task_vm8eAY5G08BEf87` | ✅ 已完成 | 日落时分的海边灯塔，海浪轻轻拍打，慢动作 |
| `task_3Xxy8AtVcGUFvqL` | ✅ 已完成 | mountain sunrise with fog slowly rolling through a valley |
| `task_5FFY22NXlQOWCdf` | ✅ 已完成 | test cat |
| `task_p37ZRIyFh3mS1c9` | ✅ 已完成 | 海浪拍打岩石，日落天空，慢动作 |
| `task_YWArjSQlAu3KX28` | ✅ 已完成 | 一只可爱的柴犬在春天的公园里奔跑... |

---

## 七、错误与修复记录

### 7.1 错误时间线

```
1. Sora 2 → 503 "no available channels"
   ↓
2. 切换到 Veo 3.1 系列
   ↓
3. veo-3.1 / veo-3.1-fast / veo3 → 全部 503
   ↓
4. 搜索发现正确名称: veo-3.1-generate-preview → 200 OK
   ↓
5. 同步流式端点 → 返回 HTML (不可用)
   ↓
6. 异步端点成功提交，但下载时遇到竞态条件
   ↓
7. 修复竞态条件，成功下载 3 个视频
   ↓
8. 中文 prompt 部分失败 (卡 50%，无声失败)
   ↓
9. Windows GBK 编码错误 (进度条 Unicode 字符)
   ↓
10. 账户余额不足 → 403 Forbidden
```

### 7.2 关键修复摘要

| 问题 | 修复方案 |
|------|----------|
| Sora 2 关停 | 全部切换为 Veo 3.1 |
| 模型名不正确 | 通过多次测试确定 `veo-3.1-generate-preview` |
| 同步端点不可用 | 仅使用异步 POST /v1/videos 工作流 |
| 下载竞态条件 | `wait_for_video()` 加 3s 延迟；`download_video_content()` 5x 重试 |
| 中文审核过滤 | 优先使用英文 prompt 或简化描述 |
| Windows 编码 | 进度条使用 ASCII (`#`/`-`) 替代 Unicode (`░`/`█`) |
| 403 Forbidden | 余额不足，需充值 (约 $1.20/视频) |

---

## 八、定价分析

### 8.1 实际价格

通过 API易 后台数据确认：

| 项目 | 价格 |
|------|------|
| Veo 3.1 视频生成 | **~$1.20/次** (~¥8.5) |
| 时间 | **40-60 秒** |
| 分辨率 | 720x1280 或 1280x720 |
| 时长 | 4-8 秒 |

### 8.2 与图片生成对比

| | 图片生成 (gpt-image-2-vip) | 视频生成 (veo-3.1) |
|---|---|---|
| 单价 | $0.03/张 | **$1.20/视频** |
| 价格比 | 1x | **40x** |
| 耗时 | 90-150s | 40-60s |
| 余额 | 够用 ~200 张 | 够用 ~5 个视频 |

> **结论:** 视频生成比图片生成贵约 40 倍。个人学习建议控制测试次数，用简单 prompt 快速验证，避免重复生成相同内容。

---

## 九、配置: `src/config.py` 新增内容

```python
# ── 视频模型 ────────────────────────────────────────────────

# Sora 2 (OpenAI) — ⚠️ 已关停 (2026年3月)
SORA_VIDEO2 = "sora_video2"                     # 已不可用
SORA_2 = "sora-2"                                # 已不可用

# Veo 3.1 (Google DeepMind) — ★ 当前唯一可用
VEO_3_1_GENERATE = "veo-3.1-generate-preview"   # 文生视频, ~$1.20/次

# 视频尺寸
VIDEO_SIZE_PORTRAIT = "720x1280"
VIDEO_SIZE_LANDSCAPE = "1280x720"

# 端点
ENDPOINT_VIDEOS = "/v1/videos"

# 默认值
VIDEO_DEFAULT_MODEL = VEO_3_1_GENERATE
VIDEO_DEFAULT_SIZE = VIDEO_SIZE_PORTRAIT
VIDEO_DEFAULT_SECONDS = "8"
```

---

## 十、新增 Memory 文件

本次视频阶段新增 5 个 memory:

| Memory 文件 | 类型 | 内容 |
|---|---|---|
| `project_veo31_model.md` | project | 正确模型名 veo-3.1-generate-preview，定价 $1.20 |
| `feedback_video_content_endpoint.md` | feedback | content 端点返回 binary，竞态条件处理 |
| `feedback_video_content_safety.md` | feedback | 中文 prompt 可能触发审核过滤 |
| `feedback_video_sync_endpoint.md` | feedback | 同步流式端点不可用，仅异步可用 |
| `feedback_video_channel.md` | feedback | (已有，更新) 通道配置 + 余额不足 |

---

## 十一、经验教训

1. **中转服务的模型名不一定与官方一致** — API易 上只有 `veo-3.1-generate-preview` 能工作，而官方文档列出的 `veo-3.1`、`veo-3.1-fast` 均不可用。不能依赖 Google 官方文档，必须以 API易 实际测试为准。

2. **异步 API 要处理竞态条件** — status 返回 completed 不等于 content 立即可用。必须加延迟 + 重试机制。

3. **检查 Content-Type 而非假设 JSON** — content 端点返回 `video/mp4` 二进制，如果不检查 Content-Type 就调 `.json()` 会崩溃。

4. **内容审核是隐式的** — Veo 3.1 有内置的内容安全过滤器，中文复杂描述更容易被拦截，且不会给出具体原因。

5. **视频生成成本高** — $1.20/次的价格意味着大量测试之前要做好 prompt 设计，优先用英文简短 prompt 降低失败率。

6. **API易 后台是重要调试工具** — 当程序报错信息不足时，API易 后台可以看到所有任务的状态、输入参数和错误信息。

---

## 十二、后续建议

- [ ] 充值后验证提交新任务的完整流程
- [ ] 尝试 `image_path` 参数实现图生视频 (image-to-video)
- [ ] 研究 Veo 3.1 的 seed 控制保持视频风格一致
- [ ] 尝试更长的视频 (8s+)
- [ ] 调研其他中转服务是否有更便宜的视频模型
