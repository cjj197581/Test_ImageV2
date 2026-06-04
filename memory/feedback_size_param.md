---
name: feedback-size-param
description: "gpt-image-2-all does NOT support the size parameter — passing it causes 400 BadRequestError; gpt-image-2-vip has 30 fixed presets, official model uses auto by default"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

不同模型对 `size` 参数的支持完全不同：

| 模型 | size 参数 | 默认值 |
|------|----------|--------|
| gpt-image-2 (官方) | 支持，16的倍数，≤3840px，宽高比≤3:1 | `"auto"` |
| gpt-image-2-all | **不支持**，通过 prompt 描述尺寸 | 不传 |
| gpt-image-2-vip | 支持，但仅限 30 档预设尺寸 | `"auto"` |

**Why:** all 模型走 ChatGPT Web 线，Web 端不支持精确尺寸参数。传入 size 会触发 `openai.BadRequestError: Unknown parameter: 'size'`。

**How to apply:** `generate_image()` 和 `edit_image()` 中，通过 `MODEL_CAPABILITIES[model]["size_param"]` 判断是否传入 size。all 模型的 `size_param` 为 False，跳过该参数。

相关: [[project-apiyi-models]]
