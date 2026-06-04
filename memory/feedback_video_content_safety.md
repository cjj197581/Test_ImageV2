---
name: feedback-video-content-safety
description: Chinese prompts may trigger Veo 3.1 content safety filters causing silent failures at 50% progress; use English prompts or simpler descriptions
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Chinese prompts can cause silent failures

When using Chinese prompts with Veo 3.1 (`veo-3.1-generate-preview`) on API易, some requests fail silently:

- Progress stops at **50%** 
- Status changes to `failed` with **no error message** (empty error field)
- No indication of what triggered the failure

**Why:** Google DeepMind's Veo 3.1 has content safety filters that appear to be more sensitive to certain Chinese-language descriptions. Exact trigger words unknown, but elaborate/literary Chinese descriptions seem more likely to fail.

## Workarounds

1. **Use English prompts** — more reliable success rate
2. **Keep prompts simple** — avoid overly descriptive/literary language
3. **Retry with rephrased prompt** — if one prompt fails at 50%, rephrase and resubmit

## Examples

| Prompt | Result |
|--------|--------|
| "一只可爱的柴犬在春天的公园里奔跑，樱花花瓣随风飘落..." | Failed at 50% |
| "海浪轻柔地拍打着白色沙滩，日落时分..." | Failed at 50% |
| "mountain sunrise with fog slowly rolling" | Success |
| "test cat" | Success |
| "日落时分的海边灯塔，海浪轻轻拍打" | Success |

**How to apply:** In `video_client.py`, error handling checks for empty error messages from failed tasks. When a task fails at 50% with no error, suggest the user rephrase the prompt (simpler and/or in English).

Related: [[project-veo31-model]]
