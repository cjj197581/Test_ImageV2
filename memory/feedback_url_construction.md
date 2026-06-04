---
name: feedback-url-construction
description: "BASE_URL already contains /v1 — constructing URLs like f\"{BASE_URL}/v1/...\" creates double /v1 prefix bugs; strip the version suffix first"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

当 `BASE_URL` 已包含 `/v1` 后缀时（如 `https://api.apiyi.com/v1`），直接拼接 `/v1/draw/completions` 会生成错误的 URL：`https://api.apiyi.com/v1/v1/draw/completions`（404）。

**Why:** `/draw/completions` 端点不在标准 OpenAI `/v1/...` 路径下，需要从根路径出发。同时标准端点如 `/v1/images/generations` 通过 SDK 自动处理了路径拼接，但手动构造 URL 时容易出错。

**How to apply:** 在 `client.py` 中计算 `_ROOT_URL`：

```python
_ROOT_URL = re.sub(r"/v\d+$", "", BASE_URL) if BASE_URL.endswith("/v1") else BASE_URL
```

然后使用 `f"{_ROOT_URL}/draw/completions"` 而非 `f"{BASE_URL}/draw/completions"`。

相关: [[feedback-fallback-detection]]
