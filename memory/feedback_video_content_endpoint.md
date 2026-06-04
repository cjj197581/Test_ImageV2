---
name: feedback-video-content-endpoint
description: "/v1/videos/{id}/content returns binary video/mp4 not JSON; needs 3s delay after status=completed; retry 5x with 3s intervals"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Content endpoint returns binary MP4

The `/v1/videos/{video_id}/content` endpoint **directly returns `video/mp4` binary data**, not JSON. This is different from other API endpoints.

**Why:** API易 follows OpenAI's video API design where the content endpoint streams raw bytes.

## Race condition after completion

After `GET /v1/videos/{id}` shows `status: "completed"`, the content endpoint may still return:

```json
{"error": "task status is IN_PROGRESS, not completed"}
```

**Why:** There's a ~3-second propagation delay between the status endpoint confirming completion and the content endpoint being ready to serve the file.

## How to apply

1. `wait_for_video()` — after detecting `status == "completed"`, adds `time.sleep(3)` before returning
2. `download_video_content()` — checks Content-Type header for `video/` AND size > 1000 bytes; retries up to 5 times with 3-second intervals
3. If Content-Type is `application/json` or video bytes are < 1000, it's an error response — retry

```python
# In download_video_content():
ct = resp.headers.get("content-type", "")
if "video/" in ct and len(resp.content) > 1000:
    return resp.content  # success
# else retry after 3s
```

Related: [[project-veo31-model]]
