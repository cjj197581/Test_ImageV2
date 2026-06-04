---
name: feedback-video-channel-config
description: "API易 video generation (Sora 2 / Veo 3.1) may return 503 \"no available channels\" — user must enable video models in their API易 group settings"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

API易 的视频生成功能可能不在默认分组中。调用 `/v1/videos` 或 `/v1/chat/completions` 传入视频模型时，可能返回 503 错误：

```
"Current group default has no available channels for model sora-2 under billing mode [pay-as-you-go, pay-per-request]"
```

**Why:** API易 的「分组管理」机制控制每个 API Key 可访问的模型集合。视频模型（sora-2、veo-3.1 等）默认可能不在用户的 default 分组中。图片模型（gpt-image-2）通常是默认开通的。

**How to apply:**
1. 视频客户端 (`video_client.py`) 定义了 `VideoChannelError` 和 `VideoUnavailableError` 自定义异常
2. `_check_video_response()` 检测 503 中的 "no available channels" 并抛出 `VideoChannelError` 附带解决指引
3. 示例脚本捕获这些异常并显示友好提示而非崩溃

**用户操作:**
1. 登录 apiyi.com 后台
2. 进入「分组管理」
3. 检查 default 分组是否包含 sora-2 / veo-3.1 模型
4. 如没有，添加到分组或联系客服

相关: [[project-apiyi-models]] [[reference-api-docs]]
