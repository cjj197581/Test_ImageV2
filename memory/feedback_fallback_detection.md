---
name: feedback-fallback-detection
description: "Error message detection for fallback logic must include Chinese keywords (不支持, 未开放) alongside English keywords (404, not found) since Chinese relay services return Chinese error messages"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

API易（以及其他中国中转服务）返回的错误消息通常是中文的。仅检测英文关键词会导致 fallback 逻辑失效。

**Why:** 实际测试中，`/draw/completions` 端点返回的错误是中文的（如"不支持此端点"），初始代码只检测 "404"、"not found" 等英文关键词，导致流式和 WebHook 示例没有正确触发降级。

**How to apply:** 在错误检测中使用多语言关键词：

```python
if any(k in err for k in ("404", "not found", "html", "不支持", "draw/completions", "未开放")):
    # 触发 fallback
```

不要只检查英文关键词。中转服务的错误消息语言取决于服务商。

相关: [[project-apiyi-models]]
