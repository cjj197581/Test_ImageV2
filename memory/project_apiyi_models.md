---
name: project-apiyi-models
description: "Detailed comparison of API易's 3 gpt-image-2 model variants and their capabilities, pricing, and limitations"
metadata: 
  node_type: memory
  type: project
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

API易 提供 gpt-image-2 的三个模型变体，各有不同的能力、价格和限制：

| 维度 | gpt-image-2 (官方) | gpt-image-2-all | gpt-image-2-vip |
|------|-------------------|-----------------|-----------------|
| 路线 | OpenAI 官方转发 | 官逆 ChatGPT Web 线 | 官逆 Codex 线 |
| 计费 | Token 计费 | $0.03/张 统一价 | $0.03/张 统一价 |
| 速度 | low 3-8s / high 200-240s | 30-60s | 90-150s |
| quality 参数 | 支持 (low/medium/high/auto) | 不支持 | 不支持 |
| size 参数 | 自定义 (16倍数, ≤3840px) | **不支持** (prompt 描述) | 30 档预设 |
| 4K | 实验性支持 | 不支持 | **正式支持** |
| Mask 修复 | 支持 | 不支持 | 不支持 |
| chat/completions | 不支持 | 支持 | 支持 |
| response_format url | 不支持 | 不支持 | **支持** |

**Why:** 三个模型对应三种不同的技术路线，覆盖不同的使用场景。官方模型质量最高但计费不可控；all 最快最便宜适合日常；vip 支持 4K 和固定尺寸适合专业场景。

**How to apply:** 在 `MODEL_CAPABILITIES` 字典中维护能力矩阵，代码通过 `_cap(model)` 查询能力来决定参数行为。

相关: [[feedback-size-param]] [[feedback-b64-format]]
