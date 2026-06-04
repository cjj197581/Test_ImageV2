---
name: project-veo31-model
description: "Correct Veo 3.1 model name is veo-3.1-generate-preview; other variants (veo-3.1, veo-3.1-fast) don't work on API易; pricing ~$1.20/video"
metadata: 
  node_type: memory
  type: project
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Correct model name

On API易, the **only** working Veo 3.1 model name is:

```
veo-3.1-generate-preview
```

The following model names all returned **503 (no available channels)** or **403 (Forbidden)**:

| Wrong Name | Error |
|---|---|
| `veo-3.1` | 503 no available channels |
| `veo-3.1-fast` | 503 no available channels |
| `veo3` | 503 no available channels |
| `veo-3.1-generate` | 503 no available channels |

**Why:** API易's internal model naming doesn't match the standard Veo 3.1 identifiers. The `-preview` suffix is required. This was discovered through trial-and-error testing — the API易 documentation is incomplete on this point.

## Pricing

**~$1.20/video** (≈¥8.5 RMB) for `veo-3.1-generate-preview`.

This is significantly more than image generation ($0.006–$0.211/image). The user's account ran out of balance after ~5-6 successful generations, confirmed by 403 Forbidden on subsequent submissions.

Speed: ~40-60 seconds per generation.

## How to apply

- `config.py`: `VEO_3_1_GENERATE = "veo-3.1-generate-preview"` is the default
- Sora 2 constants preserved but marked deprecated
- Always use `veo-3.1-generate-preview` as the model parameter

Related: [[project-sora2-discontinued]] [[feedback-video-channel-config]]
