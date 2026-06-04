---
name: feedback-b64-format
description: "API易 returns raw base64 for official gpt-image-2 but may have data: prefix for all/vip models; code must handle both formats"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

API易 relay service 不同模型返回的 b64_json 格式不同：

- **gpt-image-2 (官方转发):** 纯 base64 字符串（如 `iVBORw0KGgo...`），无 `data:` 前缀
- **gpt-image-2-all / gpt-image-2-vip (官逆):** 文档说带 `data:image/png;base64,` 前缀，但实际测试中 vip 也返回纯 base64

**Why:** 模型转发来源不同 — 官方模型直连 OpenAI，官逆模型走 ChatGPT Web/Codex 线路。decode_b64() 必须兼容两种格式。

**How to apply:** `decode_b64()` 方法先检查是否以 `data:` 开头，是则解析 MIME 类型和扩展名；否则直接 base64 decode。`download_image()` 同样需要兼容纯 base64（无 data: 前缀的 URL-like 字符串）。

相关: [[feedback-extra-body-params]]
