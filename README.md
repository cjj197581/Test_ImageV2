# Test_ImageV2 — AI 图片 & 视频生成项目

基于 [API易 (apiyi.com)](https://apiyi.com) 中转服务的 AI 图像与视频生成 Python 实战项目。

- **图片生成**: OpenAI gpt-image-2 系列 (文本→图片, 图片编辑)
- **视频生成**: Google Veo 3.1 (文本→视频)
- **批量工具**: `gen.py` 通用 CLI，一键将文件夹中的 `.txt` prompt 批量生成 `.png`

> **状态**: ✅ 已完成（2026-06-04）— 暂时封存，待日后继续。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 APIYI_API_KEY 和 BASE_URL

# 3. 运行示例
python examples/01_basic_generate.py

# 4. 批量生成图片
python gen.py "你的prompts文件夹"
```

## 项目结构

```
Test_ImageV2/
├── src/                          # 核心模块
│   ├── config.py                 # 配置 & 模型常量
│   ├── client.py                 # 图片生成客户端 (3 端点)
│   ├── utils.py                  # 解码/保存工具
│   └── video_client.py           # 视频生成客户端 (异步工作流)
│
├── examples/                     # 11 个示例脚本
│   ├── 01_basic_generate.py      # 基础文生图
│   ├── 02_multi_image.py         # 多图生成
│   ├── 03_seed_control.py        # seed 风格一致
│   ├── 04_aspect_ratios.py       # 多宽高比
│   ├── 05_chinese_text.py        # 中文文字渲染
│   ├── 06_streaming.py           # 流式响应
│   ├── 07_webhook.py             # WebHook 异步
│   ├── 08_quality_comparison.py  # 画质对比
│   ├── 09_image_editing.py       # 图片编辑
│   ├── 10_sora2_text_to_video.py # 视频生成 (单任务)
│   └── 11_sora2_async_video.py   # 视频生成 (批量并发)
│
├── gen.py                        # ★ 通用批量文生图 CLI
├── run_gen2.bat                  # 一键启动脚本
├── memory/                       # 18 个经验记忆文件
├── prompts_ppt_v50/              # 课件 prompt 示例 (15个)
│   需要生成的图片的提示词/        # 相控阵雷达课件 (5个)
│
├── APIYI_完整使用指南.md          # API易 完整 API 文档
├── FINAL_REPORT.md               # 最终总结报告
├── PROJECT_SUMMARY.md            # 图片阶段总结
├── VIDEO_SUMMARY.md              # 视频阶段总结
└── GEN_使用说明.md               # gen.py 使用说明
```

## gen.py — 批量生成工具

```bash
python gen.py <文件夹路径> [选项]

选项:
  --size SIZE       输出尺寸，默认 1792x1024 (16:9)
  --out OUT         输出目录，默认与 .txt 同目录
  --model MODEL     模型: gpt-image-2 / gpt-image-2-vip / gpt-image-2-all
  --quality QUALITY 画质: high / medium / low
  --verbose, -v     显示详细日志
```

**特性:**
- 同名输出 (`slide_01.txt` → `slide_01.png`)
- 自动跳过已生成图片
- 错误不中断，最后汇总

## 模型能力

### 图片模型

| 模型 | 中文文字 | 尺寸 | 速度 | 价格 |
|------|----------|------|------|------|
| `gpt-image-2` (官方) | ★★★★★ | 任意 | 130-240s | ~$0.21 |
| `gpt-image-2-vip` | ★★★★ | 30档 | 90-150s | $0.03 |
| `gpt-image-2-all` | ★★★ | 不支持 | 30-60s | $0.03 |

### 视频模型

| 模型 | 价格 | 速度 | 时长 |
|------|------|------|------|
| `veo-3.1-generate-preview` | ~$1.20 | 40-60s | 4-8s |

> ⚠️ **Sora 2 已于 2026年3月被 OpenAI 关停**，当前唯一可用的视频模型是 Google 的 Veo 3.1。

## 关键经验

- **extra_body 传参**: seed/quality/output_format 必须通过 `extra_body` 而非直接传参
- **base64 兼容**: 官方模型纯 base64，VIP/ALL 模型带 `data:` 前缀
- **URL 拼接**: API易的 BASE_URL 已含 `/v1`，避免重复拼接
- **视频异步流**: 仅 `POST /v1/videos` → 轮询 → 下载可用，同步流式不可用
- **竞态条件**: content 端点需 status=completed 后延迟 3s + 5x 重试
- **中文审核**: Veo 3.1 对中文复杂 prompt 可能触发内容安全过滤，建议用英文
- **Windows .bat**: 必须用 GBK 编码保存，否则中文路径乱码

更多细节见 `memory/` 目录和 `FINAL_REPORT.md`。

## 依赖

- Python 3.10+
- openai
- requests
- python-dotenv
- Pillow

## 许可证

仅供学习参考。
