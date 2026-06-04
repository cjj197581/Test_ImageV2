---
name: feedback-input-fidelity
description: Never pass input_fidelity parameter when using gpt-image-2 editing — it is auto-enabled and passing it causes errors
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

gpt-image-2 的 `/v1/images/edits` 端点自动启用 high-fidelity 模式。不要手动传入 `input_fidelity` 参数。

**Why:** 根据 API易 文档明确说明，gpt-image-2 编辑自动开启 high-fidelity。手动传入此参数可能导致 400 错误。这是 gpt-image-2 与旧版 gpt-image-1 的行为差异。

**How to apply:** 在 `edit_image()` 的 `extra_body` 构造中不包含 `input_fidelity`。代码注释中已标注 "注意: 不要传 input_fidelity！gpt-image-2 自动开启"。
