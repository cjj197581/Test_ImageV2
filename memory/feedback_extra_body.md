---
name: feedback-extra-body-params
description: "Custom parameters (seed, quality, output_format, etc.) must go through extra_body dict, not as direct kwargs to OpenAI SDK's images.generate()"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

OpenAI Python SDK 的 `client.images.generate()` 方法不接受 seed、quality、output_format、output_compression、background、moderation 等参数作为直接关键字参数。

**Why:** 这些是 gpt-image-2 的扩展参数，不在标准 DALL-E API 规范中。SDK 会拒绝未知的关键字参数，抛出 `TypeError: Images.generate() got an unexpected keyword argument 'seed'`。

**How to apply:** 在 `generate_image()` 中，始终将这些参数通过 `extra_body` 字典传递：

```python
params["extra_body"] = {
    "seed": seed,
    "quality": quality,
    "output_format": output_format,
    ...
}
```

同时，`response_format` 参数（url vs b64_json）在 API易 上不被支持，不要传入此参数。API 默认返回 b64_json。

相关: [[feedback-b64-format]] [[feedback-size-param]]
