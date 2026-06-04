---
name: project-sora2-discontinued
description: OpenAI shut down Sora 2 in March 2026; Veo 3.1 (Google) is now the recommended text-to-video model on API易
metadata: 
  node_type: memory
  type: project
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

OpenAI 于 **2026年3月24日** 正式关停 Sora 及 Sora 2 全线产品：
- Sora 独立 App (iOS/Android)
- Sora 2 模型 API
- ChatGPT 内置视频生成功能

**Why:** 财务不可持续 — 日均算力成本 ~$1500万，月消费者收入仅 ~$36.7万。存活仅 25 个月。

**当前推荐的替代方案: Veo 3.1 (Google DeepMind)**

| 模型 | 价格 | 速度 | 说明 |
|------|------|------|------|
| `veo-3.1-fast` | $0.15/次 | 30-60s | **推荐**，快速迭代 |
| `veo-3.1` | $0.25/次 | 1-2min | 更高质量 |
| `veo-3.1-landscape-fast` | $0.15/次 | 30-60s | 横屏快速版 |
| `veo-3.1-fast-fl` | $0.15/次 | 30-60s | 图生视频模式 (加 -fl 后缀) |

**How to apply:**
- 默认模型已改为 `VEO_3_1_FAST`
- config.py 中 Sora 2 常量保留但标记为 "已不可用"
- 两个示例脚本 (10/11) 已改为使用 Veo 3.1

**仍需解决:** API易 账户分组需开通视频模型通道 (见 [[feedback-video-channel-config]])

Sources:
- [澎湃新闻: OpenAI关停Sora](https://m.thepaper.cn/newsDetail_forward_32830292)
- [新京报: Sora高开低走这两年](https://m.bjnews.com.cn/detail/1774426981129309.html)
