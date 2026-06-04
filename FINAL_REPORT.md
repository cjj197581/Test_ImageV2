# Test_ImageV2 项目完整总结报告

> 项目: API易 中转服务 AI 图像 & 视频生成实战
> 日期: 2026-06-04 (最终封存)
> 跨度: Phase 1 (图片) → Phase 2 (视频) → Phase 3 (批量工具 gen.py)

---

## 一、项目目标与成果总览

通过 API易 (apiyi.com) 中转服务，完整学习并实践了：

| 能力 | 模型 | 成果 |
|------|------|------|
| 文本→图片 | gpt-image-2 / vip / all | **22 张图片**，约 40MB |
| 文本→视频 | veo-3.1-generate-preview (Google) | **8 个视频**，约 26MB |
| 批量生成工具 | gen.py (自研 CLI) | 1 个通用工具，支持任意文件夹 |

---

## 二、项目文件清单

```
Test_ImageV2/
│
├── 核心代码 (src/, 4 文件, ~42KB)
│   ├── config.py           8.7KB   配置 & 模型常量
│   ├── client.py          16KB    图片生成客户端 (3 端点)
│   ├── utils.py            2.9KB   解码/保存/下载工具
│   └── video_client.py    15KB    视频生成客户端 (异步工作流)
│
├── 示例脚本 (examples/, 11 个, ~28KB)
│   ├── 01_basic_generate.py        基础文生图
│   ├── 02_multi_image.py           多图生成
│   ├── 03_seed_control.py          seed 风格一致
│   ├── 04_aspect_ratios.py         多宽高比
│   ├── 05_chinese_text.py          中文文字渲染
│   ├── 06_streaming.py             流式响应
│   ├── 07_webhook.py               WebHook 异步
│   ├── 08_quality_comparison.py    画质对比
│   ├── 09_image_editing.py         图片编辑
│   ├── 10_sora2_text_to_video.py   单任务视频生成
│   └── 11_sora2_async_video.py    批量并发视频生成
│
├── 批量工具
│   ├── gen.py              7KB     通用批量文生图 CLI
│   ├── run_gen2.bat        80B     一键启动脚本 (GBK 编码)
│   └── batch_slides.py     2KB     课件专用批量脚本 (过渡)
│
├── 文档 (4 份, ~65KB)
│   ├── APIYI_完整使用指南.md        API易 图片+视频 API 完整指南
│   ├── PROJECT_SUMMARY.md           Phase 1 图片生成总结
│   ├── VIDEO_SUMMARY.md             Phase 2 视频生成总结
│   └── GEN_使用说明.md              gen.py 批量工具使用说明
│
├── 经验记忆 (memory/, 18 个 .md)
│   ├── user_role.md                         用户角色
│   ├── project_apiyi_models.md              三模型能力矩阵
│   ├── project_sora2_discontinued.md        Sora 2 关停记录
│   ├── project_veo31_model.md               Veo 3.1 模型名 & 定价
│   ├── feedback_extra_body.md               extra_body 传参模式
│   ├── feedback_b64_format.md               base64 格式兼容
│   ├── feedback_size_param.md               size 参数限制
│   ├── feedback_fallback_detection.md       多语言错误检测
│   ├── feedback_url_construction.md         URL 拼接防重复
│   ├── feedback_input_fidelity.md           input_fidelity 禁止传入
│   ├── feedback_video_channel.md            视频通道配置
│   ├── feedback_video_content_endpoint.md   content 端点竞态条件
│   ├── feedback_video_content_safety.md     中文审核过滤
│   ├── feedback_video_sync_endpoint.md      同步端点不可用
│   ├── feedback_windows_bat_encoding.md     .bat GBK 编码规则 ★新
│   ├── feedback_windows_unicode_print.md    Windows 终端 Unicode 崩溃 ★新
│   ├── pattern_gen_batch_cli.md             批量 CLI 设计模式 ★新
│   └── reference_api_docs.md               外部文档链接
│
├── 输出文件
│   ├── output/                   (10 图片 + 8 视频)
│   ├── 需要生成的图片的提示词/     (5 PPT 课件 prompt + 图片)
│   ├── prompts_ppt_v50/          (11 组 prompt + 图片)
│   ├── prompts_book6/            (1 组 prompt + 图片)
│   ├── output_book6/             (1 图片)
│   └── 截图文件夹                (10 张 API易 后台截图)
│
└── 配置
    ├── .env                             API Key (私密)
    ├── .env.example                     配置模板
    ├── .gitignore                       忽略规则
    └── requirements.txt                 依赖清单
```

---

## 三、关键技术路线

### 3.1 图片生成架构

```
                    ┌──────────────────────┐
                    │   src/client.py       │
                    │                      │
  prompt ──────────→│ generate_image()     │──→ PNG (base64 解码)
                    │ generate_multiple()  │
  prompt+image ────→│ edit_image()         │──→ PNG (编辑)
                    │                      │
  prompt ──────────→│ generate_chat()      │──→ PNG (对话式)
                    └──────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     /v1/images/       /v1/images/     /v1/chat/
     generations       edits           completions
```

### 3.2 视频生成架构

```
  POST /v1/videos              GET /v1/videos/{id}         GET /v1/videos/{id}/content
  ─────────────                ───────────────────         ──────────────────────────
  提交任务                     轮询状态 (每 10s)             下载视频 (binary MP4)
  → {id, status:"queued"}      → {status, progress%}       → <video/mp4 bytes>
                                      │
                                      ├── queued      → 等待
                                      ├── processing  → 继续轮询
                                      ├── completed   → 等 3s → 下载 (5x 重试)
                                      └── failed      → 报错
```

### 3.3 批量生成工具设计

```
  gen.py <folder> [--size] [--out] [--model] [--quality]
  │
  ├── 扫描 folder/*.txt
  ├── 逐个调用 client.generate_image()
  ├── 保存为 folder/<name>.png
  ├── 跳过已存在的 PNG
  └── 汇总 OK/FAIL 报告
```

---

## 四、模型对比

### 图片模型

| 模型 | 中文文字 | 尺寸 | 速度 | 价格 | 最佳用途 |
|------|----------|------|------|------|----------|
| `gpt-image-2` | ★★★★★ | 任意 | 130-240s | ~$0.21 | PPT、海报、文字密集 |
| `gpt-image-2-vip` | ★★★★ | 30 档 | 90-150s | $0.03 | 常规配图、社媒 |
| `gpt-image-2-all` | ★★★ | 不支持 | 30-60s | $0.03 | 简单配图、原型 |

### 视频模型

| 模型 | 价格 | 速度 | 状态 |
|------|------|------|------|
| `sora-2` (OpenAI) | — | — | ❌ 2026年3月关停 |
| `veo-3.1-generate-preview` (Google) | ~$1.20 | 40-60s | ✅ 唯一可用 |

---

## 五、错误全记录 (按时间线)

| # | 错误 | 根因 | 修复 |
|---|------|------|------|
| 1 | OpenAI SDK 直接传 seed 报错 | API易 不支持顶层 seed | 改用 `extra_body={"seed": N}` |
| 2 | 官逆模型 base64 带 `data:` 前缀 | gpt-image-2-all 格式不同 | `decode_b64()` 兼容两种 |
| 3 | `gpt-image-2-all` 传 size 报错 | all 模型不支持 size | 按模型能力矩阵判断是否传 size |
| 4 | fallback 检测漏掉中文错误 | 仅检查英文关键词 | 加入"不支持""未开放"等中文检测 |
| 5 | URL 拼接出现 `/v1/v1/` | BASE_URL 已含 `/v1` | `_ROOT_URL` 统一处理 |
| 6 | 编辑传入 `input_fidelity` 报错 | gpt-image-2 自动启用 | 移除该参数 |
| 7 | Sora 2 所有调用 503 | OpenAI 关停 Sora 2 | 切换 Veo 3.1 |
| 8 | `veo-3.1` / `veo-3.1-fast` 503 | API易 通道名不匹配 | 确认 `veo-3.1-generate-preview` |
| 9 | 同步流式端点返回 HTML | `/v1/chat/completions` 不支持视频 | 仅用异步 `/v1/videos` |
| 10 | content 端点返回 JSON 错误 | status=completed 后存在竞态条件 | 3s 延迟 + 5x 重试 |
| 11 | 中文 prompt 卡 50% 无声失败 | Veo 3.1 内容安全过滤器 | 英文 prompt 或简化描述 |
| 12 | Unicode 进度条 `GBK encode error` | Windows 终端无法编码 `░█` | 改用 ASCII `#-` |
| 13 | `print("✓ 完成")` 崩溃 | GBK 无法编码 U+2713 | 改用 ASCII `OK` / `FAIL` |
| 14 | `.bat` 文件中文乱码 | UTF-8 写入被 CMD 按 GBK 解析 | `encoding='gbk'` + `@chcp 65001` |
| 15 | 生成中途 403 余额不足 | high 画质 ~$0.21/张，批量消耗快 | low 画质快速验证 → high 出成品 |

---

## 六、核心经验教训

### 中转服务

1. **模型名不一定与官方一致** — API易 上 Veo 3.1 必须用 `veo-3.1-generate-preview`，官方文档的 `veo-3.1` 反而 503
2. **先小额测试再充值** — $5 足够验证一个模型，不要一次大额
3. **用 low 画质快速验证** — $0.006/张的代价试错，确认满意再用 high ($0.21/张) 出成品
4. **API易 后台是调试利器** — 程序端错误信息不完整时，后台可看到完整请求和状态

### API 设计

5. **异步 API 必须处理竞态条件** — status=completed ≠ content ready，延迟+重试是标配
6. **检查 Content-Type 而非假设 JSON** — 视频 content 端点返回 `video/mp4` 二进制
7. **错误检测必须覆盖中英文** — API易 的 403/503 经常返回中文错误消息

### Python SDK

8. **extra_body 是金标准** — seed、quality、output_format 等自定义参数全部通过 `extra_body` 传递
9. **base64 格式两套标准** — 官方模型纯 base64，官逆模型带 `data:` 前缀，必须兼容

### Windows 开发

10. **`.bat` 文件用 GBK 保存** — UTF-8 的 bat 在中文 Windows 上直接变成乱码，`@chcp 65001` 只解决输出显示
11. **终端 print 避免 Unicode 符号** — `✓✗→…` 在 GBK 终端崩溃，用 `OK`/`FAIL`/`->`/`...`
12. **Python GBK 编码是 Windows 中文环境的根因** — 所有编码问题都源于这层

---

## 七、生成物统计

### 图片 (~40MB)

| 类别 | 数量 | 文件夹 |
|------|------|--------|
| 学习示例输出 | 10 张 | `output/` |
| 相控阵雷达 PPT | 5 张 | `需要生成的图片的提示词/` |
| 其他 PPT 项目 | 11 组 | `prompts_ppt_v50/` |
| 图书封面 | 1 组 | `prompts_book6/` + `output_book6/` |

### 视频 (~26MB)

| 内容 | 尺寸 | 大小 |
|------|------|------|
| 海浪拍打岩石，日落 | 1280x720 | 1.1MB |
| 日落灯塔，海浪 | 720x1280 | 3.3MB |
| mountain sunrise fog valley | 1280x720 | 600KB |
| test cat | 720x1280 | 1.8MB |
| 柴犬春天公园 | 720x1280 | 7.7MB |

---

## 八、gen.py 批量工具

项目的最终产出是一个通用的命令行工具：

```bash
python gen.py "文件夹路径" [--size 1792x1024] [--out 输出目录] [--model ...] [--quality ...]
```

配合 `run_gen2.bat`（GBK 编码，含 `@chcp 65001 >nul`），双击即可在新文件夹上运行。

特性：
- 同名输出 (`slide_01.txt` → `slide_01.png`)
- 自动跳过已生成图片
- 错误不中断，最后汇总
- 支持尺寸/模型/画质/输出目录全参数化

---

## 九、项目状态

**已封存**。如需复用：

1. 确认 `E:\AI\Test\Test_ImageV2\.env` 中 API Key 有效
2. API易 账户有余额
3. `python gen.py "你的prompts文件夹"` 即可工作
4. 所有记忆存档在 `memory/` 目录，图文报告在项目根目录

**总计: 34 源文件 + 22 图片 + 8 视频 + 18 记忆存档**
