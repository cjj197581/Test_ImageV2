# Test_ImageV2 项目完整工作总结报告

> 作者: CJJ (cjj197581)
> GitHub: https://github.com/cjj197581/Test_ImageV2
> 日期: 2026-05-27 ~ 2026-06-06
> 平台: API易 (apiyi.com) 中转服务
> 状态: ✅ 已完成并封存

---

## 目录

1. [项目背景与目标](#一项目背景与目标)
2. [项目时间线与阶段划分](#二项目时间线与阶段划分)
3. [项目文件完整清单](#三项目文件完整清单)
4. [技术架构详解](#四技术架构详解)
5. [Phase 1: 图片生成](#五phase-1-图片生成)
6. [Phase 2: 视频生成](#六phase-2-视频生成)
7. [Phase 3: 批量 CLI 工具 gen.py](#七phase-3-批量-cli-工具-genpy)
8. [Phase 4: GitHub 上传与项目整理](#八phase-4-github-上传与项目整理)
9. [Phase 5: 参考图风格迁移](#九phase-5-参考图风格迁移)
10. [完整错误记录 16 条](#十完整错误记录-16-条)
11. [经验记忆知识库](#十一经验记忆知识库)
12. [生成物清单](#十二生成物清单)
13. [API 调用费用统计](#十三api-调用费用统计)
14. [技能与工具总结](#十四技能与工具总结)
15. [后续展望](#十五后续展望)

---

## 一、项目背景与目标

### 1.1 项目缘起

本项目是一个**个人学习型项目**，目标是：

1. 学习使用 **OpenAI gpt-image-2** (ChatGPT Images 2.0, 2026年4月22日发布) 模型进行文本→图片生成
   - gpt-image-2 是 OpenAI 最新一代图像生成模型，在中文/日文/韩文 (CJK) 文字渲染上有突破性提升 (99% 准确率)
   - 支持 3:1 到 1:3 的任意宽高比，最高 2K/4K 分辨率
   - 三种画质级别: low ($0.006, 3-8s) / medium ($0.053, 25-40s) / high ($0.211, 200s+)
2. 学习使用 **Google Veo 3.1** 模型进行文本→视频生成
   - Sora 2 已于 2026年3月被 OpenAI 关停
   - Veo 3.1 是目前 API易 上唯一可用的视频生成模型
3. 学习通过 **API易 (apiyi.com)** 国内中转服务调用上述 AI 模型
   - 国内开发者难以直接申请 OpenAI/Google API Key
   - API易 支持支付宝/微信充值，极简接入
4. 编写可复用的 Python 代码和工具，沉淀为个人知识库

### 1.2 开发者背景

| 属性 | 详情 |
|------|------|
| 身份 | 中国开发者，气象雷达相关专业背景 |
| 操作系统 | Windows (中文版)，CMD 终端 |
| Python 版本 | Python 3.11 |
| API 接入 | 通过 API易 (apiyi.com) 中转服务 |
| 无直接渠道 | 无法直接申请 OpenAI / Google API Key |
| 实战场景 | 生成气象雷达教学 PPT 课件配图、AI 技术讲解图 |
| 特殊挑战 | Windows 中文 GBK 编码、中转服务的各种兼容性问题 |
| GitHub | cjj197581 (SSH 推送) |

### 1.3 技术选型与理由

| 决策 | 选择 | 原因 |
|------|------|------|
| 语言 | Python 3.11 | AI/ML 生态成熟，openai SDK 完善 |
| AI SDK | openai (官方) + requests (备用) | SDK 兼容中转服务，requests 处理非标响应 |
| 图像模型 (主力) | gpt-image-2 (官方) | 中文文字渲染最优，支持任意尺寸和画质 |
| 图像模型 (快速) | gpt-image-2-vip | $0.03 固定价，90-150s，30 档预设尺寸 |
| 图像模型 (简单) | gpt-image-2-all | $0.03 固定价，30-60s 最快，不支持 size 参数 |
| 视频模型 | veo-3.1-generate-preview | Sora 2 已关停的唯一替代，~$1.20/视频 |
| 中转服务 | API易 (apiyi.com) | 支持支付宝/微信，国内低延迟，3 分钟跑通 |
| 版本控制 | Git + GitHub | 代码托管，SSH 推送 |
| 环境变量 | python-dotenv | .env 文件隔离敏感信息 |
| 图片处理 | Pillow | 查看/验证生成的图片 |

### 1.4 API易 服务商背景

API易 是一个国内 AI API 中转服务平台，提供多个 API 节点的访问：

| 节点 | URL | 用途 |
|------|-----|------|
| 国内主力 | `https://api.apiyi.com/v1` | OpenAI 兼容模型通用 (本项目使用) |
| 国内备选 | `https://b.apiyi.com/v1` | 主节点异常时切换 |
| 海外/VIP | `https://vip.apiyi.com/v1` | 高性能/Claude/Gemini |
| CDN 加速 | `https://api-cf.apiyi.com/v1` | 仅文本请求 |

关键特征：
- 遵循 OpenAI API 协议，可以直接使用 `openai` Python SDK
- Base URL 已包含 `/v1` 后缀，拼接端点时注意不要重复
- 账户需要通过"分组管理"开通特定模型通道
- 后台 Web 面板可查看所有 API 调用记录、任务状态、余额
- 支持 SSH/支付宝/微信充值

---

## 二、项目时间线与阶段划分

### 2.1 整体时间跨度

```
2026-05-27 ──────────────────────────────────────────── 2026-06-06
     │                                                       │
     │  Phase 1: 图片生成 (~4 天)                               │
     │  ├─ Day 1: 项目初始化, .env, requirements, gitignore    │
     │  ├─ Day 1-2: 01~07 基础示例 (7个, 逐步递进)             │
     │  ├─ Day 2-3: 08~09 进阶功能 (画质对比, 图片编辑)         │
     │  ├─ Day 3: 核心模块完善 (config/client/utils 定型)       │
     │  ├─ Day 4: APIYI_完整使用指南.md 编写                     │
     │  └─ Day 4: PROJECT_SUMMARY.md + Memory 整理              │
     │                                                       │
     │  Phase 2: 视频生成 (1 天)                                 │
     │  ├─ Sora 2 503 错误 → 搜索确认关停                        │
     │  ├─ Veo 3.1 模型名试错 (5 个名字尝试)                      │
     │  ├─ API易 后台开通视频通道                                 │
     │  ├─ src/video_client.py 编写 (三层 API 设计)              │
     │  ├─ 同步流式不可用的发现与验证                              │
     │  ├─ 竞态条件发现与 3s 延迟 + 5x 重试方案                    │
     │  ├─ examples/10~11 视频示例编写                           │
     │  ├─ 视频内容安全过滤器发现 (中文 prompt 卡 50%)            │
     │  └─ VIDEO_SUMMARY.md + Memory 更新                       │
     │                                                       │
     │  Phase 3: 批量工具 gen.py (1 天)                          │
     │  ├─ 读取"需要生成的图片的提示词/"下 5 个 slide_*.txt       │
     │  ├─ batch_slides.py (过渡脚本, 写死路径)                  │
     │  ├─ gen.py 通用 CLI 设计 (参数化, 跳过已有, 非致命错误)    │
     │  ├─ run_gen2.bat 编写 + GBK 编码调试 (两次失败)           │
     │  ├─ Unicode print 崩溃 (✓✗→) → ASCII 替代               │
     │  ├─ 余额不足 403 中断 (3/5 完成) → 充值后补生成            │
     │  └─ GEN_使用说明.md 编写                                  │
     │                                                       │
     │  Phase 4: GitHub 上传 (1 天)                              │
     │  ├─ 参考 Test_Github_Learn 项目结构                       │
     │  ├─ Git init + .gitignore 安全策略配置                    │
     │  ├─ README.md 编写 (项目介绍, 快速开始, 模型对比)          │
     │  ├─ 第一次提交: 69 个源文件 (不含 output/)                 │
     │  ├─ 用户要求也提交生成物 → 修改 .gitignore                 │
     │  ├─ 第二次提交: 45 个图片+视频文件                          │
     │  ├─ 第三次提交: README 项目结构更新                        │
     │  ├─ 创建 GitHub 空仓库 + SSH 推送                          │
     │  └─ FINAL_REPORT.md 初版                                  │
     │                                                       │
     │  Phase 5: 风格迁移 (1 天)                                  │
     │  ├─ 用户提出: 已有参考照片, 要转成动漫风格                   │
     │  ├─ 列出 10 种动漫风格供选择, 用户选吉卜力                   │
     │  ├─ 第一次尝试: /v1/images/edits → 400 Bad Request        │
     │  ├─ 第二次尝试: /v1/chat/completions + base64 → 成功!     │
     │  ├─ CDN URL 下载 (urllib 403 → requests 200)             │
     │  ├─ 响应中正则提取 image URL (markdown ![]()格式)           │
     │  ├─ style_transfer.py 工具 (8 种风格 + CLI)               │
     │  └─ 经验记忆: feedback_image_editing_workaround.md        │
     │                                                       │
     ▼                                                       ▼
   开始                                                    封存
```

---

## 三、项目文件完整清单

### 3.1 完整目录树 (116 个文件, ~96MB)

```
Test_ImageV2/
│
├── .env                              [230B]  API Key 配置 (本地私密, 不提交)
├── .env.example                      [1.3KB] 配置模板 (含注释, 提交)
├── .gitignore                        [179B]  Git 安全排除规则
├── requirements.txt                  [68B]   Python 依赖: openai, requests, python-dotenv, Pillow
│
├── README.md                         [4.6KB] GitHub 项目首页 (含快速开始, 模型对比, 架构)
├── FINAL_REPORT.md                   [41KB]  本报告 (最终版)
├── PROJECT_SUMMARY.md                [23KB]  Phase 1 图片阶段详细总结
├── VIDEO_SUMMARY.md                  [15KB]  Phase 2 视频阶段详细总结
├── GEN_使用说明.md                   [3KB]   gen.py 工具完整文档
├── APIYI_完整使用指南.md              [27KB]  API易 图片+视频 API 完整参考 (5 大端点)
│
├── gen.py                            [7KB]   通用批量文生图 CLI ★ (核心工具)
├── batch_slides.py                   [2KB]   课件专用批量脚本 (过渡性, 写死路径)
├── style_transfer.py                 [10KB]  参考图动漫风格迁移工具 ★ (8 种风格)
├── run_gen2.bat                      [80B]   gen.py 一键启动脚本 (GBK 编码)
│
├── src/                              核心模块 (4 文件, ~42KB, ~1,200 行)
│   ├── __init__.py                   [0B]    包标识文件
│   ├── config.py                     [8.7KB] 配置加载 & 所有模型常量 & 能力矩阵
│   ├── client.py                     [16KB]  图片生成客户端 (3 个 API 端点完整封装)
│   ├── utils.py                      [2.9KB] 解码/保存/下载/查看工具函数
│   └── video_client.py               [15KB]  视频生成客户端 (异步工作流 + 竞态处理)
│
├── examples/                         示例脚本 (11 个, ~28KB, 从基础到高级)
│   ├── 01_basic_generate.py          [1.2KB] 第一张图: 橘猫在窗台上
│   ├── 02_multi_image.py             [1.9KB] n=2 多图生成验证
│   ├── 03_seed_control.py            [1.3KB] seed=42 固定风格系列
│   ├── 04_aspect_ratios.py           [1.6KB] 11 种宽高比遍历测试
│   ├── 05_chinese_text.py            [2.0KB] 三场景中文文字渲染
│   ├── 06_streaming.py               [2.1KB] SSE 流式实时进度条
│   ├── 07_webhook.py                 [1.7KB] WebHook 异步回调模式
│   ├── 08_quality_comparison.py      [2.0KB] low/medium/high 三档对比
│   ├── 09_image_editing.py           [2.9KB] /edits 端点编辑 (生成参考图→编辑)
│   ├── 10_sora2_text_to_video.py     [3.5KB] 视频单任务 (提交→轮询→下载)
│   └── 11_sora2_async_video.py       [5.8KB] 视频批量并发 (两任务同时轮询)
│
├── memory/                           Claude 经验记忆备份 (19 个 .md, ~30KB)
│   ├── MEMORY.md                     [1.8KB] 记忆文件索引 (含简要说明)
│   ├── user_role.md                  [1.5KB] 开发者角色与项目上下文
│   ├── project_apiyi_models.md       [1.5KB] 三模型变体完整能力矩阵
│   ├── project_sora2_discontinued.md [1.4KB] Sora 2 关停时间线与原因
│   ├── project_veo31_model.md        [1.6KB] Veo 3.1 正确模型名 & 定价信息
│   │
│   ├── feedback_extra_body.md        [1.1KB] 自定义参数必须通过 extra_body 传递
│   ├── feedback_b64_format.md        [1.0KB] 纯 base64 vs data:前缀 两种格式
│   ├── feedback_size_param.md        [1.1KB] all 模型不支持 size 参数
│   ├── feedback_fallback_detection.md[1.1KB] 错误检测必须覆盖中英文关键词
│   ├── feedback_url_construction.md  [1.1KB] BASE_URL 拼接避免 /v1/v1/ 重复
│   ├── feedback_input_fidelity.md    [780B]  gpt-image-2 编辑禁传 input_fidelity
│   ├── feedback_video_channel.md     [1.4KB] 视频通道配置 & 余额不足处理
│   ├── feedback_video_content_endpoint.md [1.5KB] content 返回 binary MP4 + 竞态条件
│   ├── feedback_video_content_safety.md   [1.7KB] 中文 prompt 触发审核 50% 失败
│   ├── feedback_video_sync_endpoint.md    [1.5KB] Chat Completions SSE 流式不可用
│   ├── feedback_windows_bat_encoding.md   [2.0KB] .bat GBK 编码规则 (两层编码)
│   ├── feedback_windows_unicode_print.md  [2.0KB] ✓✗→ 等 Unicode 在 Win GBK 终端崩溃
│   ├── feedback_image_editing_workaround.md [2.5KB] /edits 不可用的 chat/completions 替代
│   │
│   ├── pattern_gen_batch_cli.md      [2.0KB] 批量 CLI 设计模式: 同名输出, skip-existing
│   └── reference_api_docs.md         [1.3KB] 外部参考文档链接列表
│
├── output/                           生成的文件 (14 张图 + 8 个视频, ~39MB)
│   ├── 🖼️ 学习示例图片 (10 张):
│   │   ├── cat_1779882309_0.png              1.7MB   示例1: 橘猫在窗台
│   │   ├── cn_poster_1779882482_0.png        1.5MB   示例5: "春日花语" 海报
│   │   ├── cn_label_1779882632_0.png         1.5MB   示例5: 蜂蜜产品标签
│   │   ├── cn_app_1779882784_0.png           1.2MB   示例5: "每日阅读" 启动页
│   │   ├── multi_test_1779883073_0.png       2.2MB   示例2: gpt-image-2 多图1
│   │   ├── multi_test_1779883073_1.png       2.3MB   示例2: gpt-image-2 多图2
│   │   ├── fallback_cat_1779883280_0.png     1.5MB   示例7: all 模型降级测试
│   │   ├── webhook_fallback_1779883414_0.png 1.5MB   示例7: WebHook 降级
│   │   ├── api_test_gpt-image-2_1779883807_0.png  999KB  端点验证: 官方模型
│   │   └── vip_test_gpt-image-2-vip_1779884290_0.png 2.3MB 端点验证: VIP 模型
│   │
│   ├── 🖼️ PPT 课件图片 (3 张, 在 output/ 中):
│   │   ├── slide_01_gpt-image-2_1779919735_0.png 2.4MB  PPT S1 封面 (第一版)
│   │   ├── slide_01_gpt-image-2_1779919930_0.png 2.2MB  PPT S1 封面 (最终版)
│   │   ├── slide_02_gpt-image-2_1779920084_0.png 2.3MB  PPT S2 学习路线图
│   │   └── slide_03_gpt-image-2_1779920218_0.png 2.2MB  PPT S3 传统雷达观测
│   │
│   ├── 🎨 风格迁移图片 (1 张):
│   │   └── ghibli_style.png                 2.8MB   参考照片→吉卜力风格
│   │
│   └── 🎬 视频文件 (8 个):
│       ├── veo_test_waves_1779887013.mp4            1.1MB   首次成功
│       ├── veo_retry_task_vm8eAY5_1779887643.mp4    3.3MB   灯塔+海浪 (竖屏)
│       ├── veo_retry_task_3Xxy8At_1779887692.mp4    601KB   山间日出 (横屏)
│       ├── video_async_task_3Xxy8At_1779888236.mp4  601KB   同上 (重新下载验证)
│       ├── video_async_task_5FFY22N_1779888502.mp4  1.8MB   test cat (竖屏)
│       ├── video_async_task_p37ZRIy_1779888648.mp4  1.1MB   海浪落日 (横屏)
│       ├── video_async_task_YWArjSQ_1779889330.mp4  7.7MB   柴犬春天 (竖屏)
│       └── video_async_task_YWArjSQ_1779890057.mp4  7.7MB   同上 (重复下载)
│
├── 需要生成的图片的提示词/           相控阵雷达大气科学 PPT 课件 (5 组)
│   ├── slide_01.txt [2.1KB] → slide_01.png [2.3MB]  封面: 应用介绍
│   ├── slide_02.txt [2.3KB] → slide_02.png [2.2MB]  学习路线图: 五段式
│   ├── slide_03.txt [2.3KB] → slide_03.png [2.1MB]  传统雷达观测范式
│   ├── slide_04.txt [2.3KB] → slide_04.png [2.2MB]  三类采样瓶颈
│   └── slide_05.txt [2.2KB] → slide_05.png [1.9MB]  相控阵核心思想
│
├── prompts_ppt_v50/                  AI 技术 PPT 课件 (15 组, 含 prompt + png)
│   ├── p04_skills.txt / .png              Skills Standard 技术标准图
│   ├── p05_mcp.txt / .png                 MCP 协议架构图
│   ├── p08_dgx_spark.txt / .png           NVIDIA DGX Spark 硬件架构
│   ├── p12_download_strategy.txt / .png   下载策略流程图
│   ├── p15_translation_challenges.txt/.png AI 翻译难题对比图
│   ├── p20_dual_kb.txt / .png            双知识库存储架构
│   ├── p29_radar_signal.txt / .png       雷达信号处理链路
│   ├── spar_p16_radar_arch.txt / .png    SPAR 雷达系统架构
│   ├── spar_p18_system_arch.txt / .png   系统整体架构
│   ├── spar_p28_signal_chain.txt / .png  信号处理链
│   ├── spar_p47_scan_modes.txt / .png   扫描模式总览
│   ├── spar_p73_weather_scenes.txt / .png 天气场景应用
│   ├── spar_p81_vcp_tradeoff.txt / .png  VCP 扫描策略权衡
│   ├── xband_9modes.txt / .png           X波段 9 种工作模式
│   ├── xband_dual_arch.txt / .png         双架构对比
│   └── xband_fusion_pyramid.txt / .png    多传感器融合金字塔
│
├── prompts_book6/                    图书封面 prompt (1 组)
│   └── cover_01.txt [9 行] → output_book6/cover_01.png [2.9MB]
│
└── 参考图/                            风格迁移输入
    └── P60412-151232.jpg [4.6MB]      手机实拍室内照片
```

### 3.2 文件分类统计

| 类别 | 文件数 | 总大小 | 说明 |
|------|--------|--------|------|
| Python 源文件 | 18 | ~70KB | 核心模块 4 + 示例 11 + 工具 3 |
| Markdown 文档 | 25 | ~130KB | 报告 6 + Memory 19 |
| 配置文件 | 4 | ~2KB | .env, .env.example, .gitignore, requirements.txt |
| Prompt 源文件 (.txt) | 21 | ~25KB | 课件 prompt (英文+中文) |
| 生成的 PNG 图片 | 36 | ~65MB | 学习产出 + PPT 课件 + 风格迁移 |
| 生成的 MP4 视频 | 8 | ~26MB | Veo 3.1 文本转视频 |
| 参考照片 (.jpg) | 1 | 4.6MB | 风格迁移输入 |
| 批处理文件 (.bat) | 1 | 80B | Windows 一键启动 |
| **总计** | **116** | **~96MB** | |

### 3.3 Git 提交历史

```
27eb8dd docs: update README project structure with generated output files
        └─ README.md: 24 行变更

eddebc0 Add generated images and videos as examples
        └─ 45 files: 13 PNG + 8 MP4 + 16 PPT PNGs + 5 slide PNGs + 1 book PNG
        └─ .gitignore: 移除 output/ 排除规则

e59c806 Initial commit: AI image & video generation project
        └─ 69 files: 源码 + 示例 + 文档 + memory + prompt .txt
        └─ 5,428 行新增
```

---

## 四、技术架构详解

### 4.1 系统架构图

```
                          ┌──────────────────────────┐
                          │  API易 (apiyi.com)        │
                          │  https://api.apiyi.com/v1 │
                          │                           │
                          │  分组管理 → 模型通道开通   │
                          │  后台面板 → 调用记录/状态   │
                          └──────┬───────────────────┘
                                 │ HTTPS (Bearer Token)
          ┌──────────────────────┼──────────────────────────┐
          │                      │                          │
    ┌─────▼──────┐       ┌──────▼──────┐          ┌───────▼──────┐
    │/v1/images/ │       │/v1/chat/    │          │ /v1/videos   │
    │generations │       │completions  │          │              │
    │            │       │             │          │ POST 提交     │
    │ 文生图     │       │ 对话+生图    │          │ GET  状态     │
    │ JSON       │       │ JSON        │          │ GET  content  │
    │            │       │             │          │ (binary MP4)  │
    └─────┬──────┘       └──────┬──────┘          └───────┬──────┘
          │                      │                          │
          │              ┌───────▼───────┐                  │
          │              │/v1/images/    │                  │
          │              │edits          │ (400, 不可用)    │
          │              │multipart/form │                  │
          │              └───────────────┘                  │
          │                                                │
    ┌─────▼────────────────────────────────────────────────▼──────┐
    │                     src/ (核心模块层)                         │
    │                                                             │
    │  config.py              client.py          video_client.py  │
    │  ┌────────────────┐    ┌──────────────┐   ┌──────────────┐ │
    │  │ API_KEY        │    │generate_image│   │submit_video  │ │
    │  │ BASE_URL       │    │  ()          │   │_task()       │ │
    │  │ MODEL_OFFICIAL │    │edit_image()  │   │poll_video    │ │
    │  │ MODEL_VIP      │    │generate_chat │   │_status()     │ │
    │  │ MODEL_ALL      │    │  ()          │   │wait_for      │ │
    │  │ VEO_3_1_       │    │              │   │_video()      │ │
    │  │   GENERATE     │    │_client()     │   │download_     │ │
    │  │                │    │_cap()        │   │video_content │ │
    │  │ MODEL_         │    │_ROOT_URL     │   │  ()          │ │
    │  │ CAPABILITIES   │    │              │   │              │ │
    │  │ VIDEO_         │    │_check_       │   │_check_video  │ │
    │  │ CAPABILITIES   │    │  fallback()  │   │  _response() │ │
    │  │ VIP_SIZES      │    └──────────────┘   │_download     │ │
    │  │ validate_      │                       │  _video()    │ │
    │  │   config()     │    utils.py           │_save_video   │ │
    │  └────────────────┘    ┌──────────────┐   │  _bytes()    │ │
    │                        │decode_b64()  │   └──────────────┘ │
    │                        │save_images() │                     │
    │                        │download_     │   异常:             │
    │                        │  image()     │   VideoUnavailable │
    │                        │open_images() │   Error            │
    │                        └──────────────┘   VideoChannel     │
    │                                           Error            │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                   应用层 (examples/ + CLI 工具)               │
    │                                                             │
    │  01~09 学习示例     gen.py 批量工具      style_transfer.py  │
    │  (逐步递进)        ┌─ folder/扫描       ┌─ 参考图→base64    │
    │                    ├─ *.txt→提示词      ├─ /chat/completions│
    │                    ├─ 同名.png 输出     ├─ 正则提取CDN URL  │
    │                    ├─ skip existing     ├─ 下载保存         │
    │                    └─ 汇总 OK/FAIL     └─ 8 种风格预设     │
    │                                                             │
    │  10~11 视频示例     run_gen2.bat                             │
    │  (单任务+批量)      ┌─ @chcp 65001                           │
    │                     └─ python gen.py                        │
    └─────────────────────────────────────────────────────────────┘
```

### 4.2 核心模块详细设计

#### 4.2.1 config.py (8.7KB, 224 行) — 配置中心

**环境变量加载:**
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API_KEY: str = os.getenv("API_KEY", "")
BASE_URL: str = os.getenv("BASE_URL", "https://api.chatanywhere.com.cn")
```

**3 个图片模型常量:**
```python
MODEL_OFFICIAL = "gpt-image-2"       # 官方直连, token 计费, quality 支持
MODEL_ALL = "gpt-image-2-all"        # 官逆 Web 线, $0.03/张
MODEL_VIP = "gpt-image-2-vip"        # 官逆 Codex 线, $0.03/张, 30档尺寸
```

**3 种画质:**
```python
QUALITY_LOW = "low"          # 3-8s,   $0.006  — 缩略图/原型
QUALITY_MEDIUM = "medium"    # 25-40s, $0.053  — 电商/社媒
QUALITY_HIGH = "high"        # 200s+,  $0.211  — 海报/印刷/文字密集
QUALITY_AUTO = "auto"        # 自动选择 (官方默认)
```

**输出格式:**
```python
FORMAT_PNG = "png"
FORMAT_JPEG = "jpeg"
FORMAT_WEBP = "webp"
```

**响应格式 (模型相关):**
```python
RESPONSE_B64 = "b64_json"    # base64 图片数据 (默认, 所有模型支持)
RESPONSE_URL = "url"          # HTTP URL (有效期 1 天, 仅 gpt-image-2-vip)
```

**11 种预设尺寸 (VALID_SIZES):**
```python
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
```

**6 种 2K/4K 尺寸 (SIZES_HD):**
```python
SIZES_HD = [
    "2048x2048",  # 2K 正方形
    "2048x1152",  # 2K 宽屏
    "1152x2048",  # 2K 竖屏
    "3840x2160",  # 4K 宽屏
    "2160x3840",  # 4K 竖屏
    "2880x2880",  # 4K 正方形
]
```

**VIP 模型的 30 档尺寸 (10 比例 × 3 分辨率):**
```python
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
```

**VIDEO_CAPABILITIES 视频能力矩阵:**
```python
VIDEO_CAPABILITIES = {
    SORA_VIDEO2: {
        "duration": "4/8/12/15s",
        "size": VIDEO_SIZE_PORTRAIT,  # "720x1280"
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
    },
    ...
}
```

**VIDEO_DEFAULT_* 默认值:**
```python
VIDEO_DEFAULT_MODEL = VEO_3_1_GENERATE    # "veo-3.1-generate-preview"
VIDEO_DEFAULT_SIZE = VIDEO_SIZE_PORTRAIT   # "720x1280"
VIDEO_DEFAULT_SECONDS = "8"
```

**validate_config() 配置校验:**
```python
def validate_config() -> None:
    if not API_KEY or API_KEY == "your-api-key-here":
        raise ValueError(
            "请先配置 API Key:\n"
            "  1. 复制 .env.example 为 .env\n"
            "  2. 在 .env 中填入你的 API_KEY 和 BASE_URL"
        )
```

---

#### 4.2.2 client.py (16KB, 442 行) — 图片生成客户端

**内部辅助函数:**

```python
_ROOT_URL = re.sub(r"/v\d+$", "", BASE_URL) if BASE_URL.endswith("/v1") else BASE_URL

def _client() -> OpenAI:
    """创建 OpenAI 客户端实例"""
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)

def _cap(model: str) -> dict:
    """获取模型能力字典，默认回退到 MODEL_OFFICIAL"""
    return MODEL_CAPABILITIES.get(model, MODEL_CAPABILITIES[MODEL_OFFICIAL])
```

**_ROOT_URL 的作用:**
当 BASE_URL 是 `https://api.apiyi.com/v1` 时:
- `/v1/images/edits` 直接拼接即可 (BASE_URL 已含 /v1)
- 但对于某些需要不含 /v1 的场景, `_ROOT_URL` 去除 /v1 后缀

**generate_image() — 文生图 (端点: /v1/images/generations):**

```python
def generate_image(
    prompt: str,              # 图片描述，支持中文，最长 ~1000 字符
    model: str = MODEL_OFFICIAL,
    size: str | None = None,  # 默认根据模型能力决定
    quality: str | None = None,
    output_format: str = FORMAT_PNG,
    output_compression: int | None = None,
    response_format: str | None = None,
    seed: int | None = None,
    background: str | None = None,
    moderation: str | None = None,
) -> dict[str, Any]:
```

智能默认值逻辑:
```python
# gpt-image-2-all 不支持 size → size_param=False → 不传 size
caps = _cap(model)
if size is None:
    size = caps.get("default_size") or SIZE_AUTO
if quality is None and caps.get("quality"):  # 仅官方模型支持 quality
    quality = QUALITY_AUTO

# 所有自定义参数通过 extra_body 传递
extra_body: dict[str, Any] = {}
if seed is not None:
    extra_body["seed"] = seed
if quality:
    extra_body["quality"] = quality
# ...
```

**参数→extra_body 对照表:**

| 参数 | extra_body key | 示例值 | 仅哪些模型 |
|------|---------------|--------|-----------|
| seed | `seed` | 42 | 全部 |
| quality | `quality` | "high" | 官方 |
| output_format | `output_format` | "jpeg" | 全部 |
| output_compression | `output_compression` | 80 | 全部 (仅 jpeg/webp 有效) |
| background | `background` | "opaque" | 全部 (官方不支持 transparent) |
| moderation | `moderation` | "low" | 全部 |
| ~~input_fidelity~~ | **不可传入!** | — | gpt-image-2 编辑自动启用 |

**edit_image() — 图片编辑 (端点: /v1/images/edits, API易 上返回 400):**

支持三种模式:
1. **单图参考**: `image_paths` 传 1 个文件，prompt 描述编辑方向
2. **多图融合**: `image_paths` 最多 16 个文件，prompt 中用 "图1"/"图2" 指代
3. **Mask 修复**: 指定 `mask_path` (Alpha 通道 mask 图, ≤50MB)

请求使用 `multipart/form-data` 格式:
```python
files_data: list[tuple[str, tuple[str, bytes, str]]] = []
for i, path in enumerate(image_paths):
    with open(path, "rb") as f:
        files_data.append((f"image[{i}]", (filename, f.read(), mime)))
```

**注意:** 在 API易 上此端点返回 400，实际不可用。替代方案是用 `/v1/chat/completions` 端点发送 base64 图片。

**generate_chat() — 对话式生图 (端点: /v1/chat/completions):**

仅 gpt-image-2-vip 和 gpt-image-2-all 支持此端点 (官方模型不支持 chat):
```python
def generate_chat(
    prompt: str,
    image_urls: list[str] | None = None,  # 可选的参考图 URL
    model: str = MODEL_VIP,
    size: str | None = None,
) -> dict[str, Any]:
```

构建 Chat messages:
```python
content: list[dict] = []
if image_urls:
    for url in image_urls:
        content.append({
            "type": "image_url",
            "image_url": {"url": url},
        })
content.append({"type": "text", "text": prompt})

messages = [{"role": "user", "content": content}]
```

**模型降级 (fallback) 检测:**
```python
def _check_fallback(error_msg: str) -> bool:
    """检测是否需要降级到其他模型"""
    return any(k in error_msg for k in (
        "不支持", "未开放",           # 中文
        "not supported", "not found",  # 英文
    ))
```

---

#### 4.2.3 utils.py (2.9KB, 97 行) — 工具函数

**decode_b64() — base64 双格式兼容 (核心函数):**

```python
def decode_b64(data: str) -> tuple[bytes, str]:
    """解码 base64，兼容两种格式:
    - 官方模型 (gpt-image-2): 纯 base64 "iVBORw0KGgo..."
    - VIP/ALL 模型: 带 data: 前缀 "data:image/png;base64,iVBORw0..."
    
    Returns: (图片字节数据, 扩展名)
    """
    ext = "png"
    if data.startswith("data:"):
        # 解析 "data:image/png;base64,iVBORw0..." 或 "data:image/jpeg;base64,..."
        header, b64 = data.split(",", 1)
        m = re.search(r"image/(\w+)", header)
        if m:
            ext = m.group(1)
            if ext == "jpeg":
                ext = "jpg"
        return base64.b64decode(b64), ext
    else:
        # 纯 base64
        try:
            return base64.b64decode(data), ext
        except Exception:
            return data.encode(), "txt"
```

关键细节:
- `jpeg` 扩展名统一转为 `jpg` (文件系统习惯)
- 如果解码失败返回原始字节 (防御性编程)

**save_images() — 批量保存:**

```python
def save_images(
    results: list[dict[str, Any]],
    prefix: str = "image",
) -> list[Path]:
    """批量保存生成结果到 output/ 目录.
    文件命名: {prefix}_{model_tag}_{timestamp}_{index}.{ext}
    例如: cat_gpt-image-2_1779882309_0.png
    """
```

**download_image() — 从 URL/data URL 下载:**
支持三种来源: HTTP URL, data: URL, 纯 base64

**open_images() — 用 Pillow 打开图片:**
方便快速查看生成结果

---

#### 4.2.4 video_client.py (15KB, 459 行) — 视频生成客户端

**三层 API 设计:**

```
Layer 1 (高级, 推荐):  generate_video_async()
  └─ 一步到位: submit → wait → download
  └─ 返回 {video_id, video_url, local_path, model, size, duration}

Layer 2 (中级, 灵活):  三个独立函数
  ├─ submit_video_task()     → video_id
  ├─ wait_for_video()         → status_dict (含 url)
  └─ download_video_content() → bytes (MP4)

Layer 3 (低级, 不可用):  generate_video_sync()
  └─ Chat Completions SSE 流式
  └─ API易 上返回 HTML 而非 SSE → 不可用
```

**自定义异常:**
```python
class VideoUnavailableError(Exception):
    """视频生成服务不可用 (账户未开通/分组无通道/服务暂不可用)."""
    pass

class VideoChannelError(VideoUnavailableError):
    """当前账户分组没有视频模型通道，需在 API易 后台配置.
    错误信息包含中文引导."""
    pass
```

**_check_video_response() — 503 错误检测:**
```python
def _check_video_response(resp: requests.Response) -> None:
    if resp.status_code == 503:
        try:
            body = resp.json()
            msg = body.get("error", {}).get("message", "")
        except Exception:
            msg = ""
        if "no available channels" in msg:
            raise VideoChannelError(
                "API易 当前分组没有视频模型通道。\n"
                "请登录 apiyi.com → 分组管理 → 确保分组包含视频模型。"
            )
        raise VideoUnavailableError(f"视频服务暂不可用 (503)。{msg}")
    resp.raise_for_status()
```

**submit_video_task() — 提交任务 (POST /v1/videos):**
```python
def submit_video_task(
    prompt: str,
    model: str = "sora-2",
    size: str = VIDEO_DEFAULT_SIZE,     # "720x1280"
    seconds: str = VIDEO_DEFAULT_SECONDS,  # "8"
    image_path: str | None = None,       # 可选参考图 (图生视频)
    timeout: int = 30,
) -> str:  # 返回 video_id
```

支持两种模式:
1. **文生视频**: JSON body (model, prompt, seconds, size)
2. **图生视频**: multipart/form-data (JSON fields + 图片文件)

**wait_for_video() — 异步轮询:**
```python
def wait_for_video(
    video_id: str,
    poll_interval: int = 15,   # 轮询间隔
    max_wait: int = 600,       # 最大等待 10 分钟
    verbose: bool = True,
) -> dict[str, Any]:
```

轮询逻辑:
```python
while True:
    elapsed = time.time() - start
    if elapsed > max_wait:
        raise TimeoutError(f"视频生成超时 ({max_wait}s)")

    status = poll_video_status(video_id)
    state = status.get("status", "")

    if state == "completed":
        time.sleep(3)  # ★ 关键: 等待 content 端点就绪
        return status
    elif state == "failed":
        raise RuntimeError(f"视频生成失败: {status.get('error', '未知错误')}")

    time.sleep(poll_interval)
```

**download_video_content() — 下载视频 (GET /v1/videos/{id}/content):**
```python
def download_video_content(
    video_id: str,
    timeout: int = 120,
    retries: int = 5,  # 5 次重试
) -> bytes:
```

重试判断逻辑:
```python
for attempt in range(retries):
    resp = requests.get(
        f"{BASE_URL}/videos/{video_id}/content",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=timeout,
    )
    resp.raise_for_status()

    ct = resp.headers.get("content-type", "")
    if "video/" in ct and len(resp.content) > 1000:
        return resp.content  # ← 成功: 确认是 video + 非空

    # JSON 错误或竞态条件 → 等待 3s 后重试
    if attempt < retries - 1:
        time.sleep(3)
```

这是经过实战总结的关键逻辑:
1. 检查 Content-Type 包含 `video/` (不是 JSON)
2. 检查 body 大小 > 1000 字节 (不是错误 JSON)
3. 两者都满足才返回，否则重试

**_download_video() — URL 下载 (urllib):**

用于同步流式端点返回的 video URL:
```python
def _download_video(url: str, prefix: str = "video") -> Path:
    timestamp = int(time.time())
    filepath = _OUTPUT / f"{prefix}_{timestamp}.mp4"
    urlretrieve(url, filepath)
    return filepath
```

**_save_video_bytes() — 字节保存:**
```python
def _save_video_bytes(data: bytes, video_id: str) -> Path:
    timestamp = int(time.time())
    short_id = video_id[:12]  # 截断长 ID
    filepath = _OUTPUT / f"video_async_{short_id}_{timestamp}.mp4"
    filepath.write_bytes(data)
    return filepath
```

---

### 4.3 模型能力矩阵 (完整版)

#### 图片模型 (MODEL_CAPABILITIES)

| 能力 | gpt-image-2 (官方) | gpt-image-2-vip | gpt-image-2-all |
|------|:---:|:---:|:---:|
| **quality 参数** | ✅ low/medium/high | ❌ | ❌ |
| **size 参数** | ✅ 任意 (16倍数, ≤3840px) | ✅ 30档预设 | ❌ (通过prompt描述) |
| **4K 分辨率** | ✅ (实验性) | ✅ (正式支持) | ❌ |
| **mask inpainting** | ✅ | ❌ | ❌ |
| **chat/completions** | ❌ | ✅ | ✅ |
| **response_format: url** | ❌ | ✅ (有效期1天) | ❌ |
| **默认 size** | "auto" | "auto" | None (不传) |
| **base64 格式** | 纯 base64 | `data:...;base64,` | `data:...;base64,` |
| **定价模式** | token 计费 | $0.03/张 统一价 | $0.03/张 统一价 |
| **low 价格** | ~$0.006 | — | — |
| **medium 价格** | ~$0.053 | — | — |
| **high 价格** | ~$0.211 | — | — |
| **low 速度** | 3-8s | — | — |
| **medium 速度** | 25-40s | — | — |
| **high 速度** | 200-240s | — | — |
| **VIP/ALL 速度** | — | 90-150s | 30-60s |
| **n 限制** | 1 | 1 | 1 |
| **中文文字质量** | ★★★★★ | ★★★★ | ★★★ |
| **适用场景** | 海报/印刷/中文密集 | 常规配图/社媒 | 简单配图/原型 |

#### 视频模型

| 模型 | API易 状态 | 价格 | 速度 | 时长 | 说明 |
|------|:---:|------|------|------|------|
| `sora_video2` | ❌ 503 | — | — | 4-15s | OpenAI 关停 |
| `sora_video2-landscape` | ❌ 503 | — | — | 4-15s | OpenAI 关停 |
| `sora-2` | ❌ 503 | — | — | 4-12s | 异步端点, OpenAI 关停 |
| `sora-2-pro` | ❌ 503 | — | — | 4-12s | 1080p专业级, OpenAI 关停 |
| `veo-3.1` | ❌ 503 | — | — | 8s | API易 未开通此通道 |
| `veo-3.1-fast` | ❌ 503 | — | — | 8s | API易 未开通此通道 |
| **`veo-3.1-generate-preview`** | ✅ | **~$1.20** | **40-60s** | **4-8s** | **唯一可用** |

---

## 五、Phase 1: 图片生成

### 5.1 学习路径与每步教学内容

从完全不会到能熟练调用，共编写 **9 个示例脚本**+ **3 个核心模块**:

```
01_basic_generate.py (1.2KB)
  ├─ 教学内容: 最简单的调用方式
  ├─ Prompt: "一只可爱的橙色虎斑猫坐在窗台上，阳光从窗外照进来，温暖的午后氛围"
  ├─ 参数: size="1024x1024", quality=auto (默认)
  ├─ 产出: cat_*.png (1.7MB)
  └─ 学到: generate_image() → save_images() 的基本流程

        ↓

02_multi_image.py (1.9KB)
  ├─ 教学内容: n 参数的含义和限制
  ├─ 发现: gpt-image-2 的 n 参数上限为 1 (单次只能生成 1 张)
  ├─ 要生成多张需调用多次 (而非 n=2)
  ├─ 产出: multi_test_*.png ×2 (2.2MB + 2.3MB)
  └─ 学到: API 限制与实际调用策略

        ↓

03_seed_control.py (1.3KB)
  ├─ 教学内容: seed 参数保持视觉风格一致
  ├─ seed=42, 3 个 prompt 只改变主体颜色 (黑猫/白猫/橘猫)
  ├─ Prompt: "一只可爱的{黑/白/橘}猫坐在沙发上，暖色调插画风格"
  ├─ 产出: cat_style_*.png ×3
  └─ 学到: seed 控制随机性, 系列作品技巧

        ↓

04_aspect_ratios.py (1.6KB)
  ├─ 教学内容: 遍历 11 种宽高比, 确认模型支持
  ├─ 从 "3072x1024" (3:1) 到 "1024x3072" (1:3)
  ├─ Prompt: "一张抽象的几何装饰图案，柔和渐变色，{宽}:{高} 比例"
  └─ 学到: 尺寸参数的有效范围

        ↓

05_chinese_text.py (2.0KB)
  ├─ 教学内容: gpt-image-2 的 CJK 文字渲染能力验证
  ├─ 3 个场景:
  │   ├─ 海报: "春日花语" (艺术字体)
  │   ├─ 标签: "纯天然蜂蜜" / "净含量 500g" / "产地 云南" (产品信息)
  │   └─ App: "每日阅读" / "每天进步一点点" (UI 文字)
  ├─ quality="high" (文字密集推荐高画质)
  ├─ 产出: cn_poster.png + cn_label.png + cn_app.png
  └─ 学到: 中文文字在 gpt-image-2 下的渲染效果 (99% 准确)

        ↓

06_streaming.py (2.1KB)
  ├─ 教学内容: SSE 流式响应, 实时进度
  ├─ 解析 "data: {...}" 格式的流式事件
  ├─ 事件类型: progress (进度%), status (状态变更), error (错误)
  └─ 学到: iter_lines() + json.loads() 解析 SSE

        ↓

07_webhook.py (1.7KB)
  ├─ 教学内容: WebHook 异步回调模式
  ├─ 提交任务后不阻塞, 通过回调 URL 接收结果
  └─ 学到: 异步模式的设计模式

        ↓

08_quality_comparison.py (2.0KB)
  ├─ 教学内容: low/medium/high 三档画质的实际对比
  ├─ 同一 prompt + 同一 seed → 不同 quality → 对比效果
  ├─ 对比维度: 速度 (3s/30s/200s) vs 质量 (细节/清晰度)
  └─ 学到: "low 验证 → high 定稿" 的工作策略

        ↓

09_image_editing.py (2.9KB)
  ├─ 教学内容: 基于参考图 + prompt 进行图片编辑
  ├─ Step 1: 先生成一张名片模板 (参考图)
  ├─ Step 2: 通过 edit_image() 添加文字和元素
  ├─ Prompt: "在这张名片模板上添加公司名称'星辰科技'..."
  └─ 学到: /v1/images/edits 端点的 multipart/form-data 格式
```

### 5.2 核心技术难点详解

#### 5.2.1 extra_body 传参模式 (错误 #1)

**问题描述:**
使用 openai SDK 的标准传参方式在 API易 上失败:

```python
# ❌ API易 报错: 无法识别的参数
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
client.images.generate(
    model="gpt-image-2",
    prompt="...",
    seed=42,         # ← SDK 层面传入
    quality="high",  # ← SDK 层面传入
)
```

**根因:** API易 的 OpenAI 兼容层在 SDK client 层面对参数做了严格校验，只接受 OpenAI 官方定义的参数。`seed`、`quality`、`output_format` 等 gpt-image-2 特有的参数不被 SDK 原生支持。

**修复:**
```python
# ✅ 通过 extra_body 传递所有自定义参数
client.images.generate(
    model="gpt-image-2",
    prompt="...",
    extra_body={
        "seed": 42,
        "quality": "high",
    }
)
```

**哪些参数需要走 extra_body:**

| 参数 | 在 extra_body 中? | 说明 |
|------|:---:|------|
| model | ❌ | SDK 原生参数 |
| prompt | ❌ | SDK 原生参数 |
| n | ❌ | SDK 原生参数 |
| size | ❌ | SDK 原生参数 |
| seed | ✅ | gpt-image-2 特有 |
| quality | ✅ | gpt-image-2 特有 |
| output_format | ✅ | gpt-image-2 特有 |
| output_compression | ✅ | gpt-image-2 特有 |
| background | ✅ | gpt-image-2 特有 |
| moderation | ✅ | gpt-image-2 特有 |
| response_format | ❌ (VIP 模型可用顶层) | 两处都可传 |

**重要:** 这个规则适用于 `client.images.generate()`。对于直接用 `requests` 调用的端点（如 `/v1/videos`），直接在 JSON body 中传参即可。

---

#### 5.2.2 base64 双格式兼容 (错误 #2)

**问题描述:**
用 gpt-image-2-vip 生成图片后，解码 base64 时失败:

```python
# gpt-image-2 (官方) 返回:
{"b64_json": "iVBORw0KGgo..."}
→ base64.b64decode("iVBORw0KGgo...") ✅ 成功

# gpt-image-2-vip 返回:
{"b64_json": "data:image/png;base64,iVBORw0KGgo..."}
→ base64.b64decode("data:image/png;base64,...") ❌ 失败!
```

**根因:** VIP 和 ALL 模型返回的 base64 带有 `data:image/png;base64,` 前缀（完整 Data URL 格式），而官方模型返回的是纯 base64 字符串。

**修复:** `decode_b64()` 函数检测 `data:` 前缀，自动分离 MIME 头和 base64 内容:

```python
def decode_b64(data: str) -> tuple[bytes, str]:
    if data.startswith("data:"):
        header, b64 = data.split(",", 1)
        m = re.search(r"image/(\w+)", header)
        ext = m.group(1) if m else "png"
        return base64.b64decode(b64), ext
    else:
        return base64.b64decode(data), "png"
```

**为什么会有两种格式:**
- 官方模型 (gpt-image-2): 遵循传统 DALL-E 格式, 纯 base64
- VIP/ALL 模型: 使用 Data URL 标准 (RFC 2397), 可以直接嵌入 HTML `<img src="data:image/png;base64,...">`

---

#### 5.2.3 size 参数模型限制 (错误 #3)

**问题描述:**
对 `gpt-image-2-all` 传 `size="1024x1024"` 时 API 报错。

**根因:** gpt-image-2-all 不支持 `size` 参数。尺寸通过 prompt 中的文字描述来控制（如 "square image"、"wide format"）。

**修复:** 通过 MODEL_CAPABILITIES 矩阵判断:

```python
caps = _cap(model)
if caps.get("size_param", True):  # all 模型为 False
    params["size"] = size
```

| 模型 | size_param | 传参方式 |
|------|:---:|------|
| gpt-image-2 | ✅ True | `size="1024x1024"` |
| gpt-image-2-vip | ✅ True | `size="1024x1024"` (限 30 档) |
| gpt-image-2-all | ❌ False | 不传 size, 通过 prompt 控制 |

---

#### 5.2.4 中文错误检测 (错误 #4)

**问题描述:**
fallback 逻辑（模型降级）检测错误关键词时，遗漏了中文错误消息:

```python
# ❌ 只检查英文
if "not supported" in msg or "not found" in msg:
    fallback_to_other_model()
```

API易 的 403/503 错误经常返回中文消息:
```json
{"error": {"message": "当前分组不支持此模型"}}
{"error": {"message": "该功能未开放"}}
```

**修复:**
```python
if any(k in msg for k in (
    "不支持", "未开放",           # 中文
    "not supported", "not found",  # 英文
)):
    fallback_to_other_model()
```

---

#### 5.2.5 URL 拼接防重复 (错误 #5)

**问题描述:**
```python
BASE_URL = "https://api.apiyi.com/v1"
url = f"{BASE_URL}/v1/images/generations"
# 结果: https://api.apiyi.com/v1/v1/images/generations  ← 双 /v1!
# API 返回: {"error": "Invalid URL (POST /v1/v1/images/generations)"}
```

**根因:** API易的 BASE_URL 已经包含 `/v1` 路径。如果代码中再拼接 `/v1/...`，就会出现 `/v1/v1/`。

**修复:** 使用 `_ROOT_URL` 去除 BASE_URL 的 /v1 后缀:

```python
_ROOT_URL = re.sub(r"/v\d+$", "", BASE_URL) if BASE_URL.endswith("/v1") else BASE_URL
```

然后在需要完整 URL 时直接使用 `BASE_URL + "/endpoint"`（不含 /v1 前缀）:
```python
# ✅ 正确
url = f"{BASE_URL}/images/edits"
# → https://api.apiyi.com/v1/images/edits
```

---

#### 5.2.6 input_fidelity 参数 (错误 #6)

**问题描述:**
在图片编辑时传入 `input_fidelity` 参数导致报错。

**根因:** gpt-image-2 的 `/v1/images/edits` 端点自动启用 high-fidelity（高清保真），**不允许**手动传入此参数。这是 gpt-image-2 不同于 gpt-image-1 (DALL-E 3) 的行为。

**修复:**
```python
# ❌ 不要传这个参数
extra_body["input_fidelity"] = "high"

# ✅ gpt-image-2 编辑自动启用，不需要手动指定
```

---

### 5.3 生成的图片示例

| 示例 | 文件 | 大小 | 模型 | prompt 摘要 | 教学点 |
|------|------|------|------|-----------|--------|
| 01 | cat_*.png | 1.7MB | gpt-image-2 | 橘猫窗台阳光午后 | 第一次调用全流程 |
| 02 | multi_test_* ×2 | 4.5MB | gpt-image-2 | 几何装饰图案 | n 参数限制 |
| 03 | cat_style_* ×3 | ~5MB | gpt-image-2 | 黑/白/橘猫 + seed=42 | seed 保持风格 |
| 04 | (11张宽高比) | — | gpt-image-2 | 几何图案 + 尺寸遍历 | 宽高比范围 |
| 05 | cn_poster | 1.5MB | gpt-image-2 | "春日花语"海报 | 中文文字 |
| 05 | cn_label | 1.5MB | gpt-image-2 | 蜂蜜产品标签 | 小字中文 |
| 05 | cn_app | 1.2MB | gpt-image-2 | "每日阅读"启动页 | UI 中文 |
| 08 | quality 对比 ×3 | — | gpt-image-2 | 同一 prompt, 三档质量 | 速度vs质量 |
| 09 | 编辑结果 | — | gpt-image-2 | 名片模板→添加文字 | 编辑端点 |
| — | api_test | 999KB | gpt-image-2 | API 端点连通验证 | 官方模型验证 |
| — | vip_test | 2.3MB | gpt-image-2-vip | API 端点连通验证 | VIP 模型 + url 格式 |

---

## 六、Phase 2: 视频生成

### 6.1 Sora 2 关停调查 (完整过程)

**起因:**
用户问: "听说 Sora 2 的文本到视频模型比较好" → 准备使用 Sora 2。

**第一次尝试 (所有 Sora 模型全 503):**
```
POST /v1/chat/completions + model=sora_video2 → 503 no available channels
POST /v1/chat/completions + model=sora_video2-landscape → 503
POST /v1/videos + model=sora-2 → 503
POST /v1/videos + model=sora-2-pro → 503
```

**用户回忆:**
用户想起来 "sora2 是否被 OpenAI 公司给终止了？"

**搜索确认:**
通过 WebSearch 搜索 Sora 2 最新状态，确认:
- 2026年3月24日: OpenAI 正式关停 Sora 及 Sora 2 全线产品
- 关停范围: Sora 独立 App (iOS/Android) + Sora 2 模型 API + ChatGPT 内置视频生成
- 关停原因: 财务不可持续 — 日均算力成本约 $1500 万美元, 月消费者收入仅约 $36.7 万美元
- 存活时间: 仅 25 个月 (2024年2月发布 → 2026年3月关停)

**信息来源:**
- 澎湃新闻: OpenAI关停Sora
- 新京报: Sora高开低走这两年

**结论:** Sora 2 已永久不可用。需要寻找替代方案。

---

### 6.2 Veo 3.1 模型名探索过程

切换到 Google Veo 3.1 后，最大的坑是模型命名。

**试错过程 (5 次):**

```
尝试 1: model="veo-3.1"
  → POST /v1/videos
  → 503 {"error": {"message": "no available channels"}}
  → 结论: 通道未开通

尝试 2: model="veo-3.1-fast"
  → POST /v1/videos
  → 503 {"error": {"message": "no available channels"}}
  → 结论: 快速版也未开通

尝试 3: model="veo3"
  → POST /v1/videos
  → 503 (同上)
  → 结论: 简写不存在

尝试 4: model="veo-3.1-generate"
  → 503 (同上)

尝试 5: model="veo-3.1-generate-preview"  ← ★ 成功!
  → 200 OK
  → {"id": "task_vm8eAY5...", "status": "queued"}
  → 40-60s 后完成, 成功下载 MP4
```

**关键发现:** API易 上唯一可用的 Veo 3.1 模型名是 `veo-3.1-generate-preview`。
官方 Google 文档列出的 `veo-3.1` 和 `veo-3.1-fast` 在 API易 上反而不存在。这是因为 API易 的通道命名与 Google 官方不同，`-generate-preview` 后缀是 API易 内部定义的。

**API易 后台验证:**
用户在 API易 后台看到了 `veo-3.1-generate-preview` 的正确通道 ID (1167)，确认通道已开通。

---

### 6.3 API易 后台的使用价值

在视频生成调试过程中，API易 的后台 Web 面板起到了关键作用:

**后台可以查看的信息:**
```json
{
  "action": "sora2_video_generation",
  "channel_id": 1167,
  "status": "completed",
  "progress": "100%",
  "properties": {
    "input": "{\"model\":\"veo-3.1-generate-preview\",\"prompt\":\"...\",\"seconds\":\"4\",\"size\":\"1280x720\"}",
    "ratios": {
      "billing_type": 2,
      "group_ratio": 1,
      "user_discount": 1,
      "user_group": "default"
    }
  },
  "quota": 600000,
  "result_url": "/v1/videos/task_xxx/content",
  "start_time": 1779887312,
  "finish_time": 1779887343
}
```

**后台的调试价值:**
1. 当程序返回信息不足时，后台可以看到完整的 prompt 和参数
2. 确认任务是否成功提交 (有时程序报错但任务实际已创建)
3. 查看真实的扣费情况 (billing_type, group_ratio)
4. 获取 `result_url` 用于手动下载
5. 确认任务完成时间和生成耗时

---

### 6.4 视频异步工作流 (详细版)

```
Step 1: POST /v1/videos (提交任务)
  Request:
    POST https://api.apiyi.com/v1/videos
    Headers: Authorization: Bearer {API_KEY}
    Body (JSON):
    {
      "model": "veo-3.1-generate-preview",
      "prompt": "mountain sunrise with fog slowly rolling through a valley",
      "seconds": "4",
      "size": "1280x720"
    }
  
  Response (200):
    {"id": "task_3Xxy8AtVcGUFvqLYx5r01Aa84bAq47an", "status": "queued"}
    
  或图生视频 (multipart/form-data):
    POST /v1/videos
    Headers: Authorization: Bearer {API_KEY}
    Form fields:
      model: veo-3.1-generate-preview
      prompt: ...
      seconds: 4
      size: 1280x720
    File:
      input_reference: reference.png (image/png)

Step 2: GET /v1/videos/{id} (轮询状态, 每 10-15s)
  Request:
    GET https://api.apiyi.com/v1/videos/task_3Xxy8AtVcGUFvqL...
    Headers: Authorization: Bearer {API_KEY}
  
  Response (200):
    {
      "id": "task_3Xxy8AtVcGUFvqL...",
      "status": "processing",   // queued → processing → completed / failed
      "progress": 50,           // 0-100
      "model": "veo-3.1-generate-preview",
      "object": "video"
    }

Step 3: GET /v1/videos/{id}/content (下载视频, 二进制!)
  Request:
    GET https://api.apiyi.com/v1/videos/task_3Xxy8AtVcGUFvqL.../content
    Headers: Authorization: Bearer {API_KEY}
  
  Response (200):
    Content-Type: video/mp4
    Content-Length: 614464
    Body: <binary MP4 data>

⚠️ 关键细节:
  - content 端点返回的是 video/mp4 二进制, 不是 JSON!
  - 如果 Content-Type 是 application/json → 说明是错误响应, 需要重试
  - status=completed 后 content 可能还不 ready (竞态条件):
    → wait_for_video() 在 completed 后额外等 3s
    → download_video_content() 内置 5 次重试 + 3s 间隔
```

---

### 6.5 视频生成的三个关键错误

#### 6.5.1 内容审核无声失败 (错误 #11)

**现象:**
```
GET /v1/videos/task_xxx
→ {"status": "processing", "progress": 50}
  ... (卡在 50%) ...
→ {"status": "failed", "error": ""}  ← 无任何错误信息!
```

**触发条件:**
使用复杂的中文 prompt 时容易触发:
- ❌ "一只可爱的柴犬在春天的公园里奔跑，樱花花瓣随风飘落，温暖的午后阳光透过树叶洒在地面上，慢动作，电影质感"
- ❌ "海浪轻柔地拍打着白色沙滩，日落时分天空呈现橙色和紫色的渐变，几只海鸥在远处飞翔，棕榈树的叶子在微风中摇曳，平静舒缓的氛围，自然纪录片风格"
- ✅ "mountain sunrise with fog slowly rolling through a valley"
- ✅ "test cat"
- ✅ "日落时分的海边灯塔，海浪轻轻拍打，慢动作" (简洁中文也可)

**根因:** Google Veo 3.1 的内容安全过滤器 (content safety filter) 对中文的敏感度似乎更高，特别是文学性描述较多的 prompt。

**修复策略:**
1. 优先使用英文 prompt
2. 中文 prompt 保持简洁，避免过度文学化描述
3. 如果 50% 失败，用英文重新表述后重试

---

#### 6.5.2 同步流式端点不可用 (错误 #9)

**现象:**
```
POST /v1/chat/completions + stream=True + model=veo-3.1-generate-preview
→ 响应体是 HTML 页面而非 SSE 流
```

**结论:** API易 上 Chat Completions 端点不支持视频模型的流式生成。只有异步 `/v1/videos` 端点可用。

**代码保留:** `generate_video_sync()` 函数在 `video_client.py` 中保留（标记为"备用"），以便将来 API易 支持时启用。

---

#### 6.5.3 余额不足 403 (错误 #15)

**现象:**
```
POST /v1/videos
→ 403
→ {"error": {"message": "user [65944] quota [-14305] preConsumedQuota [7500] is not enough"}}
```

**根因:** Veo 3.1 约 $1.20/次，生成 5-6 个视频后余额耗尽。用户确认"生成一个视频需要花费 1.2 美元"，充值后恢复正常。

---

### 6.6 生成的视频清单

| # | 任务 ID | 本地文件名 | 内容 | 尺寸 | 大小 | 语言 | 结果 |
|---|---------|-----------|------|------|------|------|------|
| 1 | task_... | veo_test_waves_*.mp4 | 海浪拍打岩石，日落天空 | 1280x720 | 1.1MB | 中文 | ✅ |
| 2 | task_vm8eAY5* | veo_retry_task_vm8eAY5_*.mp4 | 日落时分的海边灯塔 | 720x1280 | 3.3MB | 中文 | ✅ |
| 3 | task_3Xxy8At* | veo_retry_task_3Xxy8At_*.mp4 | mountain sunrise fog valley | 1280x720 | 600KB | 英文 | ✅ |
| 4 | task_3Xxy8At* | video_async_task_3Xxy8At_*.mp4 | 同上 (重新下载验证) | 1280x720 | 600KB | 英文 | ✅ |
| 5 | task_5FFY22* | video_async_task_5FFY22N_*.mp4 | test cat | 720x1280 | 1.8MB | 英文 | ✅ |
| 6 | task_p37ZRIy* | video_async_task_p37ZRIy_*.mp4 | 海浪拍打岩石，日落天空，慢动作 | 1280x720 | 1.1MB | 中文 | ✅ |
| 7 | task_YWArjSQ* | video_async_task_YWArjSQ_*.mp4 | 柴犬在春天公园里奔跑 | 720x1280 | 7.7MB | 中文 | ✅ |

---

## 七、Phase 3: 批量 CLI 工具 gen.py

### 7.1 需求背景

用户有 5 个 `.txt` 文件（slide_01~05），每个包含约 800 字的详细 PPT 课件 prompt。需要:

1. 将每个 `.txt` 读为 prompt
2. 用 gpt-image-2 + high + 1792x1024 生成对应 PNG
3. 输出文件名与 `.txt` 同名（`slide_01.txt` → `slide_01.png`）
4. 如果 PNG 已经存在则跳过（节省 API 费用）
5. 一个失败不影响后续
6. Windows CMD 环境下可运行

### 7.2 开发过程

**第一版: batch_slides.py (过渡性)**
- 写死文件夹路径
- 只支持这一组特定的 prompt
- 用于验证批量生成可行性

**遇到问题:**
- Windows GBK 终端: `print("✓ 完成")` 崩溃 → 改为 `print("OK")`
- 余额不足: 第 3 张后 403 → 需要 skip-existing 功能
- 中文文件夹路径: `glob("需要生成的图片的提示词/*.txt")` 在 Python 中正常，但 .bat 中乱码

**第二版: gen.py (通用 CLI)**
- 参数化: folder (必选), size/model/quality/out (可选)
- 同名输出: `{name}.txt` → `{name}.png`
- 智能跳过: 生成前检查 PNG 是否已存在
- 非致命错误: try/except 包裹每个生成，最后汇总
- 所有中文 print 替换为英文/ASCII

### 7.3 gen.py 完整命令行接口

```bash
python gen.py <folder> [选项]

位置参数:
  folder              包含 .txt prompt 文件的文件夹路径

可选参数:
  --size SIZE         输出尺寸, 默认 1792x1024 (16:9)
                      常用: 1024x1024, 1280x720, 2048x1152
  --out OUT           输出文件夹, 默认与 .txt 同目录
  --model MODEL       模型: gpt-image-2 / gpt-image-2-vip / gpt-image-2-all
                      默认: gpt-image-2 (官方, 中文最优)
  --quality QUALITY   画质: high / medium / low
                      默认: high
  --verbose, -v       显示详细保存路径

示例:
  python gen.py "需要生成的图片的提示词"
  python gen.py "prompts" --size 1024x1024
  python gen.py "prompts" --size 1792x1024 --out ./slides
  python gen.py "prompts" --model gpt-image-2-vip --quality low
```

### 7.4 gen.py 核心实现

```python
def main():
    # 1. 解析文件夹 (支持相对/绝对路径, 中文)
    folder = Path(args.folder)
    if not folder.is_absolute():
        folder = (Path(__file__).resolve().parent / folder).resolve()

    # 2. 扫描 .txt 文件
    txt_files = sorted(f for f in os.listdir(str(folder))
                       if f.endswith(".txt"))

    # 3. 逐文件生成
    for txt_path in txt_files:
        name = txt_path.stem  # "slide_01"
        
        # 3a. 跳过已存在的 PNG
        existing = out_dir / f"{name}.png"
        if existing.exists():
            print(f"[{i}/{total}] {name} -> SKIP (already exists)")
            continue
        
        # 3b. 读取 prompt, 调用 API
        prompt = txt_path.read_text(encoding="utf-8").strip()
        result = generate_image(prompt=prompt, model=..., size=..., quality=...)
        
        # 3c. 解码并保存
        img_bytes, ext = decode_b64(result["b64_json"])
        png_path = out_dir / f"{name}.png"
        png_path.write_bytes(img_bytes)
    
    # 4. 汇总
    print(f"Done! {len(ok)} ok, {len(fail)} fail")
```

### 7.5 Windows 编码问题深度解析

#### 7.5.1 Windows CMD 编码模型 (两层编码)

```
                              用户看到
                                 ▲
                                 │ 第二层: 终端显示
                                 │ chcp 65001 → UTF-8
                                 │ chcp 936   → GBK (默认)
                                 │
                            ┌────┴────┐
                            │  CMD.EXE │
                            └────┬────┘
                                 │ 第一层: 文件解析
                                 │ 始终使用系统 ANSI (GBK/cp936)
                                 │ 解析 .bat 文件内容
                                 │
                            ┌────┴────┐
                            │ .bat 文件│
                            └─────────┘
```

**关键认知:** `chcp 65001` 只影响第二层 (输出显示)，不影响第一层 (文件解析)。
CMD 始终用 GBK (cp936) 解析 `.bat` 文件中的字符。如果 `.bat` 是 UTF-8 编码:
- 第一层解析时就已经乱码了
- 第二层切换到 UTF-8 也无济于事

#### 7.5.2 run_gen2.bat 的正确写法

```batch
@chcp 65001 >nul
python gen.py  "需要生成的图片的提示词"
PAUSE
```

保存编码: **GBK / ANSI** (Windows 记事本默认编码)

编码验证:
```python
# ✅ 正确: 用 GBK 编码写入
with open("run_gen2.bat", "w", encoding="gbk") as f:
    f.write(content)

# ❌ 错误: 用 UTF-8 写入
with open("run_gen2.bat", "w", encoding="utf-8") as f:
    f.write(content)  # CMD 按 GBK 解析 → 乱码!
```

#### 7.5.3 Unicode print() 崩溃

Python stdout 在 Windows CMD 下默认编码是 GBK (cp936):

```python
# ❌ 崩溃
print("✓ 完成 (163s) → output/slide_01.png")
# UnicodeEncodeError: 'gbk' codec can't encode character '✓'

# ✅ 正常
print("OK (163s) -> output/slide_01.png")
```

**哪些 Unicode 字符在 GBK 中不可用:**

| 字符 | Unicode | GBK 支持? | 替代 |
|------|---------|:---:|------|
| ✓ (CHECK MARK) | U+2713 | ❌ | OK |
| ✗ (BALLOT X) | U+2717 | ❌ | FAIL |
| → (RIGHTWARDS ARROW) | U+2192 | ❌ | -> |
| … (HORIZONTAL ELLIPSIS) | U+2026 | ❌ | ... |
| — (EM DASH) | U+2014 | ❌ | -- |
| ' (LEFT SINGLE QUOTE) | U+2018 | ❌ | ' |
| ' (RIGHT SINGLE QUOTE) | U+2019 | ❌ | ' |
| ★ (BLACK STAR) | U+2605 | ❌ | * |
| 中文汉字 | U+4E00+ | ✅ | 不变 |

---

### 7.6 批量生成结果

使用 `python gen.py "需要生成的图片的提示词"` (或双击 run_gen2.bat):

| # | 文件 | 内容概要 | 耗时 | 状态 |
|---|------|---------|------|:---:|
| 1 | slide_01.png | 封面: 相控阵雷达在大气科学中的应用 | 163s (第一批) / 再次运行 SKIP | ✅ |
| 2 | slide_02.png | 学习路线图: 五段式流程 | 154s | ✅ |
| 3 | slide_03.png | 传统反射面天气雷达的观测范式 | 134s | ✅ |
| 4 | slide_04.png | 机械惯性带来的三类采样瓶颈 | (充值后) | ✅ |
| 5 | slide_05.png | 相控阵雷达核心思想: 相位控制波束 | (充值后) | ✅ |

**中断情况:** slide_01~03 在第一批中成功 (3/5)。余额不足导致 slide_04/05 失败 (#15)。用户充值后重新运行，skip-existing 机制跳过 slide_01~03，仅生成 slide_04/05。

---

## 八、Phase 4: GitHub 上传与项目整理

### 8.1 参考模板: Test_Github_Learn

用户之前已经成功上传过一个学习项目 `Test_Github_Learn`：

```
Test_Github_Learn/
├── .github/workflows/
│   ├── ci.yml            # 主流水线: lint → test(2版本) → build
│   ├── schedule.yml      # 定时任务: 每天自动检查
│   └── release.yml       # 自动发版: 推送 v* 标签触发
├── main.py               # 主程序
├── test_main.py          # 单元测试 (4个用例)
├── README.md             # 含 CI 徽章
└── 学习总结.md / .html    # 双格式学习手册
```

GitHub 配置:
- 账号: cjj197581
- 邮箱: cjj81@vip.163.com
- 推送方式: SSH (`git@github.com:cjj197581/...`)
- 远程: `origin  git@github.com:cjj197581/Test_Github_Learn.git`

### 8.2 .gitignore 安全策略演变

**初始版 (.gitignore 第一版):**
```gitignore
.env                    # API Key (绝对不能提交)
__pycache__/
*.py[cod]
output/*.png            # 生成的图片 (二进制)
output/*.jpg
output/*.webp
output/*.mp4            # 生成的视频 (二进制)
```

**安全审查发现的问题:**
1. `.env` 已排除 ✅
2. 但 API易 后台截图文件夹含账户余额、用户名等信息
3. 项目根目录还有其他含用户信息的文件

**最终版 (.gitignore):**
```gitignore
# 环境变量 (含 API Key，绝对不能提交)
.env

# Python
__pycache__/
*.py[cod]
*.egg-info/

# 各 prompt 文件夹中生成的 PNG (如需展示可取消注释)
# 需要生成的图片的提示词/*.png
# prompts_ppt_v50/*.png
# prompts_book6/*.png

# API易 后台截图 (含账户信息)  ← ★ 关键防护
*API易*/*
*apiyi*/
*截图*/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
```

**用户要求提交生成物后:**
移除 `output/` 排除规则 → 提交所有 output/ 中的图片和视频。

**最终提交安全确认:**
```
✅ .env                   未提交 (含 API Key)
✅ API易 截图文件夹       未提交 (含账户余额等)
✅ __pycache__/           未提交 (系统生成)
✅ output/               已提交 (用户要求)
✅ 需要生成的图片的提示词/  .png 已提交 (用户要求)
✅ 参考图/                未提交 (含用户个人照片)
```

### 8.3 GitHub 操作完整流程

```bash
# 1. Git 初始化
cd E:\AI\Test\Test_ImageV2
git init
git config user.name "cjj197581"
git config user.email "cjj81@vip.163.com"

# 2. 编写 .gitignore 和 README.md

# 3. 首次提交 (69 个源文件, 不含生成物)
git add .env.example .gitignore requirements.txt
git add src/ examples/ memory/
git add "需要生成的图片的提示词/"slide_*.txt
git add prompts_ppt_v50/*.txt prompts_book6/*.txt
git add *.md gen.py batch_slides.py run_gen2.bat
git status --short  # 检查是否有不该提交的文件
git commit -m "Initial commit: AI image & video generation project"
# → e59c806: 69 files, 5428 insertions

# 3. 用户要求提交生成物
# 修改 .gitignore → 移除 output/ 排除
git add .gitignore output/ output_book6/
git add "需要生成的图片的提示词/" prompts_ppt_v50/ prompts_book6/
git commit -m "Add generated images and videos as examples"
# → eddebc0: 45 files (PNG + MP4)

# 4. 更新 README
git add README.md
git commit -m "docs: update README project structure with generated output files"
# → 27eb8dd: 1 file, 24 lines

# 5. 创建 GitHub 仓库并推送
# (用户在 github.com 上手动创建空仓库 Test_ImageV2)
git remote add origin git@github.com:cjj197581/Test_ImageV2.git
git branch -M main
git push -u origin main
# → 全部推送成功
```

**分支改名说明:** GitHub 默认分支名为 `main`，而 `git init` 默认创建 `master`。需要 `git branch -M main` 将本地分支改名以匹配。

---

## 九、Phase 5: 参考图风格迁移

### 9.1 需求

用户: "如果我已经有了一张参考图片，怎么让你把它换一个风格来继续绘制？例如更换成某种动漫风格。"

参考图: `参考图/P60412-151232.jpg` (4.6MB 手机实拍照片)

### 9.2 动漫风格调研

为用户列出了 10 种知名动漫风格供选择:

| # | 风格 | 工作室/导演 | 特点 |
|---|------|-----------|------|
| 1 | 吉卜力/宫崎骏 | Studio Ghibli | 温暖手绘、水彩背景、自然色调 |
| 2 | 新海诚 | Makoto Shinkai | 极致写实背景、强烈光影、镜头光晕 |
| 3 | 鬼灭之刃 | Ufotable | 精致线条、浮世绘特效、电影级 |
| 4 | 龙珠/鸟山明 | Toei | 粗线条、高饱和、80年代少年漫 |
| 5 | 赛博朋克边缘行者 | Studio Trigger | 霓虹色调、高对比、扳机社硬朗 |
| 6 | 海贼王 | 尾田荣一郎 | 夸张比例、独特造型、明快色彩 |
| 7 | 京阿尼 | Kyoto Animation | 极致细腻、柔和光影、文艺复兴美学 |
| 8 | 进击的巨人 | WIT Studio | 粗犷线条、暗沉调色、写实比例 |
| 9 | 美少女战士 | 90年代少女漫 | 闪亮大眼、柔和色调、浪漫氛围 |
| 10 | JOJO | 荒木飛呂彦 | 时装插画风、硬朗轮廓、波普配色 |

用户选择了 **吉卜力/宫崎骏** 风格。

### 9.3 第一次尝试: /v1/images/edits (失败)

```python
from src.client import edit_image

result = edit_image(
    prompt=(
        "Transform this photo into Studio Ghibli anime style. "
        "Soft hand-drawn watercolor look, warm natural lighting with golden glow, "
        "gentle pastel color palette, slightly dreamy atmosphere..."
    ),
    image_paths=[r"E:\AI\Test\Test_ImageV2\参考图\P60412-151232.jpg"],
    model=MODEL_OFFICIAL,  # "gpt-image-2"
    size="1024x1024",
)
# → requests.exceptions.HTTPError: 400 Client Error: Bad Request
#   for url: https://api.apiyi.com/v1/images/edits
```

**结论:** API易 的 `/v1/images/edits` 端点返回 400。根据之前的经验（例 9 中也遇到过），该端点尚未开放。

### 9.4 第二次尝试: /v1/chat/completions + base64 (成功)

**思路转换:** 既然 `/edits` 不可用，而 `gpt-image-2-vip` 支持 chat/completions 端点且可以输入图片，那就通过 chat 端点发送 base64 图片 + 风格描述 prompt。

**实现:**
```python
import base64, requests
from src.config import API_KEY, BASE_URL, MODEL_VIP

# 1. 读取参考图并转为 base64
with open(r"E:\AI\Test\Test_ImageV2\参考图\P60412-151232.jpg", "rb") as f:
    raw = f.read()
b64 = base64.b64encode(raw).decode()
# b64 长度: 6,323,064 字符 (4.6MB 原图)

# 2. 通过 chat/completions 发送
resp = requests.post(
    f"{BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL_VIP,  # "gpt-image-2-vip" — 不能用官方模型
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                },
                {
                    "type": "text",
                    "text": (
                        "Redraw this photo as Studio Ghibli anime style. "
                        "Warm hand-drawn watercolor look, soft natural golden lighting, "
                        "gentle pastel color palette, dreamy atmosphere..."
                    )
                }
            ]
        }]
    },
    timeout=300,
)
# → 200 OK

# 3. 从响应中提取图片 URL
data = resp.json()
content = data["choices"][0]["message"]["content"]
# content: "![image](https://files.chatgpt-topup.com/files/xxx.png)\n\nHere's..."

import re
m = re.search(r"!\[.*?\]\((https?://[^\)]+)\)", content)
img_url = m.group(1)
# img_url: "https://files.chatgpt-topup.com/files/1a99d86f-430c-44f5-b06d-c00b1466c93b.png"

# 4. 下载图片
time.sleep(2)  # CDN 传播延迟
img_resp = requests.get(img_url, timeout=60)
with open("output/ghibli_style.png", "wb") as f:
    f.write(img_resp.content)
# → 2.8MB PNG
```

**关键细节:**

1. **必须用 VIP 模型** — `gpt-image-2` (官方) 不支持 chat/completions 端点
2. **base64 长度约 630 万字符** — 4.6MB 原图编码后被 API 正常接受
3. **响应中的图片 URL 在 Markdown 格式中** — `![image](url)` 需要正则提取
4. **CDN 下载有延迟** — 第一次用 urllib 报 403 (可能临时权限)，sleep 2s 后用 requests 成功
5. **CDN 域名:** `files.chatgpt-topup.com` — API易 的 CDN 服务器

### 9.5 style_transfer.py 工具设计

最终编写的通用工具支持 8 种预设风格 + 自定义图片路径 + 自定义输出路径:

```bash
python style_transfer.py                          # 默认吉卜力
python style_transfer.py --style shinkai          # 新海诚
python style_transfer.py --style ufotable         # 鬼灭之刃
python style_transfer.py --style cyberpunk        # 赛博朋克
python style_transfer.py --style kyoani           # 京阿尼
python style_transfer.py --style onepiece         # 海贼王
python style_transfer.py --style jojo             # JOJO
python style_transfer.py --style aot              # 进击的巨人
python style_transfer.py --image "照片.jpg"       # 指定图片
python style_transfer.py --list                   # 列出所有风格
python style_transfer.py --out "output/my.png"    # 指定输出
```

**8 种风格的 prompt 工程:**

每个风格都精心编写了 ~3 句英文描述，涵盖:
- 笔触/线条风格 (hand-drawn watercolor / photorealistic / sharp precise / bold thick)
- 光影特征 (soft natural golden / dramatic lens flares / dynamic lighting / neon-drenched)
- 色彩调色 (gentle pastels / vibrant saturated / bold pop-art / muted earthy)
- 氛围情感 (nostalgic whimsical / cinematic / gritty / elegant)
- 参考作品 (Spirited Away / Your Name / Demon Slayer / etc.)

**风格切换实现:**
```python
STYLES = {
    "ghibli": {
        "name": "Studio Ghibli (吉卜力/宫崎骏)",
        "prompt": "Redraw this photo as Studio Ghibli anime style. "
                  "Warm hand-drawn watercolor look, soft natural golden lighting, "
                  "gentle pastel color palette, dreamy atmosphere, "
                  "clean cel-shaded outlines, nostalgic and whimsical feeling "
                  "like Spirited Away or My Neighbor Totoro. Keep the same composition."
    },
    # ... 7 个其他风格
}
```

### 9.6 CDN 下载的小坑

第一次尝试用 Python 的 `urllib.request.urlretrieve()` 下载 CDN 图片时报 403 Forbidden:

```python
# ❌ urllib 403
urlretrieve(cdn_url, local_path)
# → HTTPError: HTTP Error 403: Forbidden

# ✅ requests 200
resp = requests.get(cdn_url)
with open(local_path, "wb") as f:
    f.write(resp.content)
```

`requests` 库发送的 HTTP 头与 `urllib` 略有不同（User-Agent 等），CDN 对 `urllib` 的默认 User-Agent 返回 403。

---

## 十、完整错误记录 (16 条)

按时间线排列，每个错误包含完整的现象→排查→根因→修复→学到的教训：

### 错误 #1: SDK 直接传 seed 报错
- **阶段:** Phase 1 (图片)
- **现象:** `client.images.generate(model=..., seed=42)` → 报错 "unexpected parameter: seed"
- **排查:** 检查 openai SDK 文档 → 发现 seed 不是 SDK 原生参数
- **根因:** API易 的 OpenAI 兼容层在 SDK 层面对参数做严格校验，只接受 OpenAI 官方定义的参数。`seed`/`quality`/`output_format` 等是 gpt-image-2 特有参数
- **修复:** 改用 `extra_body={"seed": 42, "quality": "high"}` 传递所有自定义参数
- **教训:** 中转服务的 SDK 兼容层 ≠ 原生 API。自定义参数全部走 extra_body

### 错误 #2: VIP 模型 base64 解码失败
- **阶段:** Phase 1 (图片)
- **现象:** `base64.b64decode(vip_result["b64_json"])` → binascii.Error
- **排查:** 打印 b64_json 前 50 字符 → 发现 `data:image/png;base64,` 前缀
- **根因:** gpt-image-2-vip 返回 Data URL 格式 (RFC 2397)，而非纯 base64
- **修复:** `decode_b64()` 函数检测 `data:` 前缀并自动分离 MIME 头和内容
- **教训:** 不同模型的 base64 格式不同。官方=纯 b64，VIP/ALL=Data URL

### 错误 #3: gpt-image-2-all 传 size 报错
- **阶段:** Phase 1 (图片)
- **现象:** `model="gpt-image-2-all", size="1024x1024"` → 400 错误
- **排查:** 搜索 API易 文档 → 发现 all 模型"尺寸通过 prompt 描述"
- **根因:** gpt-image-2-all 的 API 实现不支持 `size` 参数
- **修复:** 按 MODEL_CAPABILITIES 矩阵判断是否传 size
- **教训:** 中转服务的三个模型变体能力不同，需要精确的能力矩阵

### 错误 #4: fallback 漏掉中文错误关键词
- **阶段:** Phase 1 (图片)
- **现象:** API 返回中文错误 `"当前分组不支持此模型"`，但 fallback 逻辑未触发
- **排查:** 检查 fallback 检测代码 → 只匹配了英文 "not supported"
- **根因:** API易 的错误消息经常是中英文混合的
- **修复:** 同时匹配中文关键词: `"不支持"`, `"未开放"`
- **教训:** 面向中国用户的 API 错误检测必须覆盖中文

### 错误 #5: URL 出现 /v1/v1/ 重复
- **阶段:** Phase 1 (图片)
- **现象:** `POST /v1/v1/images/generations` → 404 "Invalid URL"
- **排查:** 打印完整 URL → 发现 BASE_URL 已含 /v1，代码又拼了 /v1
- **根因:** `BASE_URL="https://api.apiyi.com/v1"` + `"/v1/images/generations"` = `/v1/v1/...`
- **修复:** 使用 `_ROOT_URL` 去除 /v1 后缀；或直接拼接不带 /v1 的路径
- **教训:** 使用中转服务前先确认 BASE_URL 是否已含版本路径

### 错误 #6: 编辑传入 input_fidelity 报错
- **阶段:** Phase 1 (图片)
- **现象:** 在 `/v1/images/edits` 中传入 `input_fidelity: "high"` → 400 错误
- **排查:** 检查 gpt-image-2 文档 → 发现编辑端点"自动启用 high-fidelity"
- **根因:** gpt-image-2 不同于 gpt-image-1 (DALL-E 3)，编辑自动启用高清保真
- **修复:** 移除 `input_fidelity` 参数
- **教训:** gpt-image-2 的行为与 gpt-image-1 不完全兼容

### 错误 #7: Sora 2 全部 503
- **阶段:** Phase 2 (视频)
- **现象:** 所有 Sora 2 模型名 → 503 "no available channels"
- **排查:** 用户回忆 "sora2 是否被关停" → 搜索确认
- **根因:** OpenAI 2026年3月24日关停 Sora 全系列（日均成本 $1500万 vs 月收入 $36.7万）
- **修复:** 切换到 Google Veo 3.1
- **教训:** 使用第三方模型前确认其运营状态

### 错误 #8: Veo 3.1 模型名全部 503 (4 次)
- **阶段:** Phase 2 (视频)
- **现象:** `veo-3.1` / `veo-3.1-fast` / `veo3` / `veo-3.1-generate` → 全部 503
- **排查:** 逐一尝试不同命名格式 → 第 5 次尝试成功
- **根因:** API易 的 Veo 3.1 通道名为 `veo-3.1-generate-preview`，不同于 Google 官方命名
- **修复:** 使用 `veo-3.1-generate-preview`
- **教训:** 中转服务的模型命名可能与官方不同，需实际测试确认

### 错误 #9: 视频同步流式返回 HTML
- **阶段:** Phase 2 (视频)
- **现象:** `POST /v1/chat/completions + stream=True` → 返回 HTML 页面而非 SSE
- **排查:** 尝试不同端点格式 → 均失败
- **根因:** API易 上 Chat Completions 端点不支持视频流式生成
- **修复:** 仅使用异步 `/v1/videos` 三步工作流
- **教训:** Chat Completions SSE ≠ 视频可用入口

### 错误 #10: content 端点竞态条件
- **阶段:** Phase 2 (视频)
- **现象:** status=completed 后立即调用 content → 返回 `{"error":"task status is IN_PROGRESS, not completed"}`
- **排查:** 确认 status 已 completed → 怀疑内容端点有延迟
- **根因:** status 端点和 content 端点之间存在约 3 秒的传播延迟
- **修复:** wait_for_video() 在 completed 后加 `time.sleep(3)`；download_video_content() 5x 重试 + 3s 间隔
- **教训:** 异步 API 始终需要处理竞态条件

### 错误 #11: 中文 prompt 触发内容安全过滤
- **阶段:** Phase 2 (视频)
- **现象:** 某些中文 prompt → progress 卡在 50% → status=failed (无错误信息)
- **排查:** 对比成功/失败的 prompt → 发现文学性描述较多的中文 prompt 失败率高
- **根因:** Google Veo 3.1 内容安全过滤器对中文复杂描述的敏感度更高
- **修复:** 使用英文 prompt 或简化中文描述
- **教训:** 跨语言 AI 模型可能有隐式的内容审核差异

### 错误 #12: Unicode 进度条 (░█) GBK 崩溃
- **阶段:** Phase 3 (批量)
- **现象:** `print("  Progress: [░░░░████] 50%")` → UnicodeEncodeError
- **根因:** `░` (U+2591) 和 `█` (U+2588) 不在 GBK 字符集中
- **修复:** 使用 ASCII: `print("  Progress: [----####] 50%")`

### 错误 #13: print("✓ 完成") Unicode 崩溃
- **阶段:** Phase 3 (批量)
- **现象:** `print("✓ 完成 (163s) → file.png")` → UnicodeEncodeError
- **根因:** `✓` (U+2713), `→` (U+2192) 不在 GBK 中
- **修复:** 使用 ASCII: `print("OK (163s) -> file.png")`

### 错误 #14: .bat UTF-8 中文乱码
- **阶段:** Phase 3 (批量)
- **现象:** 双击 run_gen.bat → `'���' is not recognized as a command`
- **排查:** 用 UTF-8 编码写了 .bat → CMD 用 GBK 解析时字符错位
- **根因:** CMD 始终用系统 ANSI (GBK) 解析 .bat 文件内容, `@chcp 65001` 在解析之后才生效
- **修复:** 用 `encoding='gbk'` 保存 .bat
- **教训:** .bat 文件的编码必须是 GBK/ANSI，两层编码模型是关键认知

### 错误 #15: 生成中途 403 余额不足
- **阶段:** Phase 3 (批量)
- **现象:** 生成 3 张 high 画质 PPT 后 → `403 quota [-14305] preConsumedQuota [7500] is not enough`
- **根因:** high 画质 ~$0.21/张，Veo 3.1 ~$1.20/视频，多次调用耗尽约 $10 余额
- **修复:** 充值后继续；gen.py 的 skip-existing 机制让重新运行只生成缺失的
- **教训:** 批量生成前估算费用；low 画质验证 prompt → high 出成品的策略

### 错误 #16: /v1/images/edits → 400
- **阶段:** Phase 5 (风格迁移)
- **现象:** 发送参考图到 `/v1/images/edits` → 400 Bad Request (非 JSON 错误)
- **排查:** 检查请求格式 → multipart/form-data 格式正确 → 怀疑端点未开放
- **根因:** API易 未开放 `/v1/images/edits` 端点
- **修复:** 改用 `/v1/chat/completions` + base64 image_url
- **教训:** 编辑端点不可用, chat/completions + base64 是万能替代

---

## 十一、经验记忆知识库

### 11.1 记忆文件总览 (19 个)

| 分类 | 文件名 | 对应错误 | 核心内容 |
|------|--------|:---:|------|
| **项目** | user_role.md | — | 中国开发者在 API易 学习 gpt-image-2/Veo 3.1 |
| | project_apiyi_models.md | — | 官方/all/vip 三模型能力/价格/速度完整对比 |
| | project_sora2_discontinued.md | #7 | Sora 2 2026年3月关停, 存活25个月, 财务不可持续 |
| | project_veo31_model.md | #8 | 唯一可用模型名: `veo-3.1-generate-preview`, ~$1.20/视频 |
| **反馈** | feedback_extra_body.md | #1 | seed/quality/output_format 必须走 extra_body |
| | feedback_b64_format.md | #2 | 官方=纯b64, VIP/ALL=Data URL |
| | feedback_size_param.md | #3 | all 模型不支持 size 参数 |
| | feedback_fallback_detection.md | #4 | 中文错误关键词不可或缺 |
| | feedback_url_construction.md | #5 | BASE_URL 已含 /v1, 防重复拼接 |
| | feedback_input_fidelity.md | #6 | gpt-image-2 编辑禁传此参数 |
| | feedback_video_channel.md | #7,8,15 | 通道开通 + 余额不足处理 |
| | feedback_video_content_endpoint.md | #10 | video/mp4 二进制 + 3s 延迟 + 5x 重试 |
| | feedback_video_content_safety.md | #11 | 中文复杂 prompt 触发审核 50% 静默失败 |
| | feedback_video_sync_endpoint.md | #9 | SSE 流式视频不可用 |
| | feedback_windows_bat_encoding.md | #14 | .bat GBK 保存 + @chcp 65001 + 两层编码模型 |
| | feedback_windows_unicode_print.md | #12,13 | ✓✗→… 在 GBK 终端崩溃, 一律用 ASCII |
| | feedback_image_editing_workaround.md | #16 | /edits 不可用 → chat/completions + base64 |
| **模式** | pattern_gen_batch_cli.md | — | 批量 CLI 设计范式: 同名输出, skip-existing, 非致命错误 |
| | reference_api_docs.md | — | API易/Google/OpenAI 官方文档链接 |

### 11.2 记忆文件同步

所有 memory 文件同时存在于两个位置:
- **Claude 记忆目录:** `C:\Users\CJJ_SHY\.claude\projects\E--AI-Test-Test-ImageV2\memory\`
- **项目备份目录:** `E:\AI\Test\Test_ImageV2\memory\`

---

## 十二、生成物清单

### 12.1 图片 (36 张, ~65MB)

| 来源 | 数量 | 大小 | 用途 |
|------|:---:|------|------|
| `output/` 学习示例 | 10 | ~17MB | 从 01 基础到 09 编辑的递进学习产出 |
| `output/` 课件 | 3 | ~6.9MB | batch_slides.py 生成的 slide_01~03 |
| `output/` 风格迁移 | 1 | 2.8MB | ghibli_style.png (吉卜力) |
| `需要生成的图片的提示词/` | 5 | ~11.2MB | 相控阵雷达大气科学 PPT 5 页 |
| `prompts_ppt_v50/` | 15 | ~31MB | AI 技术 PPT 课件 15 页 |
| `output_book6/` | 1 | 2.9MB | 图书封面 |

### 12.2 视频 (8 个, ~26MB)

| 文件名 | 任务 ID | 大小 | 内容 | 语言 |
|--------|---------|------|------|:---:|
| veo_test_waves_*.mp4 | (首次成功) | 1.1MB | 海浪拍打岩石，日落天空 | 中文 |
| veo_retry_task_vm8eAY5_*.mp4 | task_vm8eAY5* | 3.3MB | 日落时分的海边灯塔 | 中文 |
| veo_retry_task_3Xxy8At_*.mp4 | task_3Xxy8At* | 601KB | mountain sunrise fog valley | 英文 |
| video_async_task_3Xxy8At_*.mp4 | task_3Xxy8At* (重下) | 601KB | 同上 (重新下载) | 英文 |
| video_async_task_5FFY22N_*.mp4 | task_5FFY22* | 1.8MB | test cat | 英文 |
| video_async_task_p37ZRIy_*.mp4 | task_p37ZRIy* | 1.1MB | 海浪拍打岩石，日落天空 | 中文 |
| video_async_task_YWArjSQ_*.mp4 | task_YWArjSQ* | 7.7MB | 柴犬在春天公园奔跑 | 中文 |
| video_async_task_YWArjSQ_*.mp4 | task_YWArjSQ* (重复) | 7.7MB | 同上 (重复下载) | 中文 |

### 12.3 Prompt 源文件 (21 个, ~25KB)

所有 prompt 以 `.txt` 格式存储，UTF-8 编码，与生成的 PNG 同名同目录。

**5 个中文 PPT 课件 prompt (slide_01~05):**
- 每个约 800-900 字符，指定了背景色系、构图布局、文字内容、科学表达要求
- 主题: 相控阵雷达在大气科学中的应用

**15 个英文 PPT 课件 prompt (prompts_ppt_v50):**
- 每个约 1 行（单行文件），简洁的技术图描述
- 主题: AI/ML 技术、雷达系统架构、信号处理、扫描模式

**1 个图书封面 prompt (prompts_book6):**
- 9 行，描述书籍封面设计

---

## 十三、API 调用费用统计

### 13.1 图片生成费用

| 操作 | 模型 | 画质 | 单次价格 | 次数(约) | 小计 |
|------|------|------|----------|:---:|------|
| 基础学习测试 | gpt-image-2 | auto | ~$0.03 | 5 | $0.15 |
| 多图生成 | gpt-image-2 | auto | ~$0.03 | 2 | $0.06 |
| seed 系列 | gpt-image-2 | auto | ~$0.03 | 3 | $0.09 |
| 宽高比遍历 | gpt-image-2 | auto | ~$0.03 | 11 | $0.33 |
| 中文文字测试 | gpt-image-2 | high | ~$0.21 | 3 | $0.63 |
| 画质对比 | gpt-image-2 | low/med/high | 混合 | 3 | $0.27 |
| 模型降级测试 | gpt-image-2-all | — | $0.03 | 2 | $0.06 |
| 端点验证 | gpt-image-2 + vip | — | 混合 | 2 | $0.06 |
| PPT 课件 (batch) | gpt-image-2 | high | ~$0.21 | 5 | $1.05 |
| 风格迁移 | gpt-image-2-vip | — | $0.03 | 2 | $0.06 |
| **图片小计** | | | | **~38** | **~$2.76** |

### 13.2 视频生成费用

| 操作 | 模型 | 单次价格 | 次数 | 小计 |
|------|------|----------|:---:|------|
| 成功生成 | veo-3.1-generate-preview | ~$1.20 | 8 | $9.60 |
| **视频小计** | | | **8** | **$9.60** |

### 13.3 总计

| 类别 | 调用次数 | 费用 |
|------|:---:|------|
| 图片生成 | ~38 | ~$2.76 |
| 视频生成 | 8 | ~$9.60 |
| **合计** | **~46** | **~$12.36** (~¥88 RMB) |

### 13.4 费用优化建议

1. **low 画质先验证** → 确认 prompt 和布局 → high 出成品 (省 97%)
2. **使用 VIP 模型** → 复杂 prompt 先 low 验证, 简单场景直接用 VIP ($0.03 统一价)
3. **视频优先用英文** → 降低 content safety filter 误杀 (失败也扣费?)
4. **skip-existing 机制** → 中断后继续不重复生成

---

## 十四、技能与工具总结

### 14.1 产出的可复用工具

| 工具 | 文件 | 大小 | 能力 |
|------|------|------|------|
| **gen.py** | gen.py | 7KB | 通用批量文生图 CLI: 文件夹→同名PNG, 参数化, skip-existing |
| **style_transfer.py** | style_transfer.py | 10KB | 图片转动漫风格: 8种预设, chat/completions + base64 |
| **run_gen2.bat** | run_gen2.bat | 80B | Windows 一键启动 (GBK 编码, @chcp 65001) |

### 14.2 核心模块 (可复用的库)

| 模块 | 功能 | 行数 |
|------|------|:---:|
| `src/config.py` | 模型常量, 能力矩阵, 尺寸定义, 端点 URL, 配置校验 | 224 |
| `src/client.py` | 3 个 API 端点封装, extra_body 管理, 模型降级 | 442 |
| `src/utils.py` | base64 双格式解码, 批量保存, URL 下载 | 97 |
| `src/video_client.py` | 异步视频工作流, 竞态处理, 三层 API 设计 | 459 |

### 14.3 掌握的技术能力

1. **OpenAI SDK + 中转服务适配**
   - extra_body 传参模式 (seed/quality/output_format/background/moderation)
   - base64 双格式兼容 (纯 b64 vs Data URL)
   - 按模型能力矩阵决策传参 (size_param, quality, response_format)
   - URL 拼接规则 (BASE_URL 的 /v1 后缀处理)

2. **异步视频 API 设计**
   - 三步工作流: POST submit → GET poll → GET content
   - 竞态条件处理: status=completed + 3s delay + 5x retry
   - Content-Type 检测: 确认 video/mp4 而非 JSON 再返回
   - 内容安全过滤器的应对策略

3. **Windows 中文环境适配**
   - .bat 文件的两层编码模型 (解析层 GBK + 输出层 chcp 65001)
   - Unicode 字符的 GBK 冲突表 (✓✗→…★ 等)
   - 中文文件夹路径在 Python/CMD/Git 中的处理

4. **批量 CLI 工具设计**
   - 同名输出 (slide_01.txt → slide_01.png)
   - skip-existing 节省费用
   - 非致命错误汇总
   - 参数化设计 (folder/size/model/quality/out/verbose)

5. **Git/GitHub 安全工作流**
   - .gitignore 分层安全策略
   - SSH 推送 + branch 改名 (master→main)
   - 敏感信息审查 (.env, 截图, 个人照片)

6. **风格迁移技术**
   - chat/completions + base64 image_url 作为 /edits 的替代
   - 正则提取 CDN URL (Markdown ![]()格式)
   - CDN 下载的 User-Agent 兼容问题

---

## 十五、后续展望

### 15.1 可继续探索的方向

- [ ] **图生视频 (Image-to-Video):** `submit_video_task(image_path=...)` 参数已实现，待测试。将参考图转为 4-8s 短视频
- [ ] **视频风格一致性:** Veo 3.1 是否支持 seed 控制？能否生成系列视频？
- [ ] **/v1/draw/completions 端点:** API易 文档提到但未测试，支持流式+WebHook
- [ ] **批量视频工具:** 类似 gen.py 的视频批量生成 CLI
- [ ] **CI/CD:** GitHub Actions 自动测试 API 端点可用性 (定期 check)
- [ ] **费用监控:** 在 gen.py 中加入费用估算和余额检查
- [ ] **更便宜的视频服务:** 调研其他中转服务的 Veo 3.1 定价
- [ ] **Prompt 模板库:** 将成功的 prompt 整理为可复用的模板
- [ ] **GUI 工具:** 用 tkinter 或 Web UI 让非技术用户也能使用

### 15.2 项目复用指南

```bash
# 1. 克隆项目
git clone git@github.com:cjj197581/Test_ImageV2.git
cd Test_ImageV2

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env:
#   API_KEY=sk-你的API易Key
#   BASE_URL=https://api.apiyi.com/v1

# 4. 使用 gen.py 批量生成
python gen.py "你的prompts文件夹"
python gen.py "prompts" --size 1024x1024 --quality medium

# 5. 使用 style_transfer.py 风格迁移
python style_transfer.py --style ghibli
python style_transfer.py --image "照片.jpg" --style cyberpunk

# 6. 运行学习示例
python examples/01_basic_generate.py
```

---

## 附录 A: 关键数据一览

| 指标 | 数值 |
|------|------|
| 项目周期 | 11 天 (2026-05-27 ~ 2026-06-06) |
| 总文件数 | 116 |
| Python 代码行数 | ~2,600 行 (18 个 .py 文件) |
| Markdown 文档 | 25 篇 (~130KB) |
| 经验记忆 | 19 个 |
| 示例脚本 | 11 个 |
| 生成图片 | 36 张 (~65MB) |
| 生成视频 | 8 个 (~26MB) |
| Prompt 源文件 | 21 个 (~25KB) |
| API 调用总次数 | ~46 |
| 总费用 | ~$12.36 (~¥88 RMB) |
| 踩过的坑 | 16 个 |
| Git 提交 | 3 次 |
| GitHub 仓库 | github.com/cjj197581/Test_ImageV2 |
| API 端点 | 4 个 (generations, edits, chat/completions, videos) |
| 模型 | 4 个 (official, vip, all, veo-3.1-generate-preview) |

---

## 附录 B: 配置文件模板 (.env.example)

```bash
# API易 配置
# 复制此文件为 .env 并填入你的信息

# API Key (从 apiyi.com 获取)
API_KEY=your-api-key-here

# Base URL (API易 国内节点)
BASE_URL=https://api.apiyi.com/v1
```

---

## 附录 C: 术语对照表

| 术语 | 全称 | 说明 |
|------|------|------|
| API易 | apiyi.com | 国内 AI API 中转服务平台 |
| gpt-image-2 | ChatGPT Images 2.0 | OpenAI 2026年4月发布的图像生成模型 |
| Veo 3.1 | — | Google DeepMind 的视频生成模型 |
| extra_body | — | openai SDK 中传递非标准参数的字典 |
| SSE | Server-Sent Events | 流式响应的数据格式 |
| b64 | base64 | 二进制数据的文本编码 |
| GBK | GB2312 扩展 | 中文 Windows 系统默认编码 |
| ANSI | — | Windows 上对系统默认编码的称呼 (实际是 GBK) |
| chcp | Change Code Page | Windows 命令, 切换终端编码页 |
| 65001 | — | UTF-8 的 Windows 代码页号 |
| CDN | Content Delivery Network | 内容分发网络 |

---

## 附录 D: 所有命令速查

```bash
# 批量生成图片
python gen.py "文件夹" [--size WxH] [--out DIR] [--model M] [--quality Q] [--verbose]

# 风格迁移
python style_transfer.py [--style S] [--image PATH] [--list]

# 视频生成 (单任务)
python examples/10_sora2_text_to_video.py

# 视频生成 (批量)
python examples/11_sora2_async_video.py

# 单个学习示例
python examples/01_basic_generate.py
# ... 02 ~ 09

# Windows 一键启动
run_gen2.bat
```

---

**项目状态: ✅ 已完成并封存 (2026-06-06)**
