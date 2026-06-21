# Test_ImageV2 下一阶段待开展工作

> 项目当前状态: ✅ 已完成并封存 (2026-06-06)
> 本文档列出尚未实验成功、需要在下一阶段继续探索的工作

---

## 一、概述

本项目在 11 天内完成了核心功能的开发和验证：
- ✅ 图片生成: 3 个模型变体, 11 个示例, 通用批量工具 gen.py
- ✅ 视频生成: Veo 3.1 异步工作流, 单任务+批量示例
- ✅ 风格迁移: chat/completions + base64 方案, 1/8 风格验证

但仍有许多功能和方向尚未探索。本文档系统梳理待开展工作，作为下一阶段的路线图。

---

## 二、图片生成 - 待探索

### 2.1 画质与格式 (未系统测试)

| 功能 | 当前状态 | 待做 |
|------|----------|------|
| low 画质全场景 | 仅 08 示例测试 1 张 | 用 low 验证 gen.py 生成的每张 prompt |
| medium 画质 | 仅 08 示例 | 评估 medium 是否足够 PPT 使用 (省钱) |
| jpeg 输出格式 | **未测试** | `output_format="jpeg"` + `output_compression=80` |
| webp 输出格式 | **未测试** | 体积 vs 质量对比 |
| output_compression | **未测试** | 0-100 范围的实际效果 |
| background=opaque | **未测试** | 与默认 auto 的区别 |
| moderation 参数 | **未测试** | low/auto 两种级别的影响 |

### 2.2 4K 分辨率 (未测试)

```python
# 待验证:
generate_image(model=MODEL_OFFICIAL, size="3840x2160")     # 4K 宽屏
generate_image(model=MODEL_OFFICIAL, size="2160x3840")     # 4K 竖屏
generate_image(model=MODEL_VIP, size="3840x2560")          # VIP 4K 3:2
```

需确认: API易 是否支持 4K，价格是否与官方文档一致，生成时间是否可接受。

### 2.3 VIP 模型 30 档尺寸 (仅测试了默认)

VIP 模型支持 10 个比例 × 3 个分辨率档位，目前只用过 `1024x1024` 和 `1792x1024`。
建议系统遍历测试 30 档，建立速度/质量数据库。

### 2.4 /v1/images/edits 端点 (API易 上 400)

- 联系 API易 客服确认该端点是否开放
- 如开放，验证三种模式: 单图参考、多图融合 (最多 16 张)、Mask 修复 (Alpha 通道)
- 如不开放，继续使用 chat/completions + base64 替代

### 2.5 /v1/draw/completions 端点 (从未测试)

API易 文档提到 `/v1/draw/completions` 是新端点，支持:
- 流式响应 (SSE 实时进度)
- WebHook 异步回调
- 可能支持更高的并发和更低的延迟

需验证: 此端点是否在 API易 上开放，与 `/v1/images/generations` 的区别。

### 2.6 多图融合 (最多 16 张)

```python
# 从未测试: 通过 chat/completions 发送多张参考图
messages = [{
    "role": "user",
    "content": [
        {"type": "image_url", "image_url": {"url": f"data:...;base64,{b64_1}"}},
        {"type": "image_url", "image_url": {"url": f"data:...;base64,{b64_2}"}},
        {"type": "text", "text": "融合图1的风格和图2的内容..."}
    ]
}]
```

---

## 三、视频生成 - 待探索

### 3.1 图生视频 Image-to-Video (未测试)

`video_client.py` 的 `submit_video_task()` 已支持 `image_path` 参数，但从未实际调用:

```python
# 待验证:
submit_video_task(
    prompt="make this scene animated with gentle movement",
    model=VEO_3_1_GENERATE,
    image_path="参考图/P60412-151232.jpg",  # ← 图生视频
    seconds="4",
    size="1280x720",
)
```

需确认:
- API易 是否支持 veo-3.1-generate-preview 的图生视频
- 图生视频的价格是否与文生视频相同
- 图片格式要求 (jpg/png/webp, 最大分辨率)

### 3.2 视频时长 (仅测试了 4s/8s)

```python
# 待测试:
submit_video_task(seconds="8")    # 8s 视频
submit_video_task(seconds="12")   # 是否支持 12s?
```

Veo 3.1 的最大时长未确认，API易 可能限制在 8s。

### 3.3 视频质量/seed (未测试)

- Veo 3.1 是否支持 seed 参数保持视频风格一致？
- 是否支持 quality 参数？
- 视频分辨率: 720p 和 1080p 的实际画质差异

### 3.4 批量视频生成工具 (不存在)

类似 `gen.py` 的视频版本:
```bash
python gen_video.py "video_prompts/" --model veo-3.1-generate-preview --size 1280x720
```

需考虑:
- 视频成本高 (~$1.20/个)，需要费用预估和确认提示
- 并发提交策略 (同时提交多个 vs 顺序提交)
- 视频轮询的并发管理

### 3.5 更多 Veo 3.1 模型变体 (未发现)

- 搜索 API易 是否陆续开通了其他 Veo 变体
- `veo-3.1-generate` (非 preview), `veo-3.1-fast`
- 是否有 Veo 3.2 或更新版本

### 3.6 音视频同步

API易 文档未提及音频，但 Veo 3.1 官方支持同步音频:
- 生成的视频是否包含音频？
- 如包含，音频质量如何？
- 是否可以通过 prompt 控制音频内容？

---

## 四、风格迁移 - 待探索

### 4.1 其余 7 种风格验证

目前只验证了吉卜力风格。待逐一测试:
- [ ] shinkai (新海诚)
- [ ] ufotable (鬼灭之刃)
- [ ] cyberpunk (赛博朋克)
- [ ] kyoani (京阿尼)
- [ ] onepiece (海贼王)
- [ ] jojo (JOJO)
- [ ] aot (进击的巨人)

测试维度: 生成速度, 风格还原度, CDN URL 稳定性, 对中文原图的适应性。

### 4.2 局部风格迁移 (未测试)

不是全局转换，而是局部修改:
```python
# Prompt 工程方向:
"Keep the background as is, but redraw the person in anime style"
"Only change the lighting to Ghibli-style warm glow, keep everything else"
```

### 4.3 风格融合 (未测试)

融合两种风格:
```python
"Redraw as a blend of Ghibli watercolor background + Cyberpunk neon highlights"
```

### 4.4 风格迁移 + 视频 (未测试)

先将照片转为动漫风格，再用图生视频生成动态版本。
这是一个完整的内容生产管线: 照片 → 动漫 → 视频。

---

## 五、基础设施和工具

### 5.1 GitHub Actions (不存在)

参考 Test_Github_Learn 项目的 CI/CD 经验:
```yaml
# .github/workflows/api_check.yml
# 每日定时检查 API易 端点可用性
# 发现 503/403 时自动通知
```

### 5.2 费用预估功能

gen.py 中加余额检查和费用预估:
```python
python gen.py "prompts" --dry-run
# 输出: 5 个 .txt, 预计费用 $1.05 (high) / $0.15 (low)
# 确认后输入 yes 继续
```

### 5.3 自动重试机制

gen.py 和 style_transfer.py 中:
- 当前: 失败后标记 FAIL，不重试
- 改进: 余额不足自动降级模型/画质；网络错误自动重试 3 次

### 5.4 GUI 或 Web 界面

为不熟悉命令行的用户提供界面:
- tkinter 桌面 GUI
- 或简单的 HTML/JS Web 界面 + Flask 后端
- 功能: 拖入文件夹 → 选择模型/尺寸 → 点击生成 → 预览结果

### 5.5 Prompt 模板库

将验证成功的 prompt 整理为模板:
```
prompt_templates/
├── ppt_slide_16x9.txt       # PPT 横版模板
├── poster_chinese.txt        # 中文海报模板
├── tech_diagram.txt          # 技术图表模板
└── anime_ghibli.txt          # 吉卜力风格模板
```

---

## 六、其他中转服务调研

### 6.1 价格对比

| 服务 | 图片价格 | 视频价格 | 是否测试 |
|------|---------|---------|:---:|
| API易 (apiyi.com) | $0.006~0.211 | ~$1.20 | ✅ |
| ChatAnywhere | 有免费 Key | ? | ❌ |
| 诗云API (shuyunapi.com) | 新用户送 50 元 | ? | ❌ |
| 其他 | ? | ? | ❌ |

### 6.2 模型覆盖

- API易 是否支持 Claude 模型用于图片理解？
- API易 的 Gemini 原生端点是否可用？
- 是否有 FLUX / Seedream / Stable Diffusion 等开源模型的 API？

---

## 七、未完成的实验记录

| # | 实验 | 状态 | 备注 |
|---|------|:---:|------|
| 1 | Sora 2 全系列 | ❌ 关停 | OpenAI 2026.3.24 关停 |
| 2 | veo-3.1 / veo-3.1-fast | ❌ 503 | API易 未开通这些通道 |
| 3 | 视频同步流式 SSE | ❌ HTML | API易 不支持 |
| 4 | /v1/images/edits | ❌ 400 | API易 未开放 |
| 5 | slide_04/slide_05 首批 | ❌ 403 | 余额不足, 充值后补生成 |
| 6 | Veo 3.1 图生视频 | ⏳ 未测 | 代码已就绪 |
| 7 | VIP 30 档尺寸遍历 | ⏳ 未测 | |
| 8 | 4K 分辨率 | ⏳ 未测 | |
| 9 | /v1/draw/completions | ⏳ 未测 | |
| 10 | 视频 seed 控制 | ⏳ 未测 | |
| 11 | jpeg/webp 格式 | ⏳ 未测 | |
| 12 | 多图融合 (16张) | ⏳ 未测 | |
| 13 | 其他动漫风格 (7种) | ⏳ 未测 | 仅吉卜力已验证 |
| 14 | GitHub Actions CI | ⏳ 未建 | |
| 15 | 批量视频工具 | ⏳ 未建 | |
| 16 | 费用预估/dry-run | ⏳ 未建 | |

---

## 八、下一阶段建议优先级

### 高优先级 (投入少, 收益大)
1. **低画质验证策略** — 将 gen.py 的默认改为 `--quality low`，出成品时手动切换到 high
2. **风格迁移其余 7 种** — 逐一运行 `style_transfer.py --style X`
3. **图生视频** — 验证 `submit_video_task(image_path=...)` 是否可用
4. **GitHub Actions** — 自动化 API 端点可用性检查

### 中优先级 (需要一定投入)
5. **费用预估 dry-run** — 批量生成前的成本预览
6. **批量视频工具** — 类似 gen.py 的视频版本
7. **VIP 30 档尺寸遍历** — 建立尺寸-速度数据库
8. **其他中转服务调研** — 寻找更便宜的视频方案

### 低优先级 (长期或可选)
9. **4K 分辨率测试** — 成本高, 等有实际需求再测
10. **GUI/Web 界面** — 非个人使用需求
11. **多图融合** — 等 /edits 端点或 chat 端点确认支持
12. **Prompt 模板库** — 随使用积累

---

## 九、快速恢复实验

```bash
# 下一阶段开始时，在项目目录执行:
cd E:\AI\Test\Test_ImageV2

# 1. 确认 API 可用
python -c "from src.config import validate_config; validate_config()"

# 2. 测试图生视频
python examples/10_sora2_text_to_video.py  # 修改为传 image_path

# 3. 测试其他动漫风格
python style_transfer.py --style cyberpunk
python style_transfer.py --style shinkai

# 4. 低画质批量生成
python gen.py "需要生成的图片的提示词" --quality low

# 5. 检查余额
# 登录 apiyi.com 后台查看
```
