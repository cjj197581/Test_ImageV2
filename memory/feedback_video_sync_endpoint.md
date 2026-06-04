---
name: feedback-video-sync-endpoint
description: API易 video sync streaming via /v1/chat/completions returns HTML not SSE; only async POST /v1/videos → poll → download workflow works
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## Sync streaming endpoint is non-functional for video

Attempting to generate videos through the Chat Completions SSE streaming endpoint (`POST /v1/chat/completions` with `stream=True`) fails:

- Some endpoints return **HTML** instead of SSE JSON
- Others return non-standard response formats
- Even with correct model names, no video URL is extracted from the stream

**Why:** API易's implementation of the video API only fully supports the async workflow (`/v1/videos`). The Chat Completions path may work for some models but not for `veo-3.1-generate-preview`.

## How to apply

- `generate_video_sync()` in `video_client.py` is kept for reference/future use but is known to be non-functional
- `generate_video_async()` using the 3-step workflow is the **production-recommended** path
- All example scripts use the async workflow exclusively

## Working workflow (async only)

```
POST   /v1/videos              → {"id": "task_xxx", "status": "queued"}
GET    /v1/videos/{id}         → {"status": "processing", "progress": 50}
GET    /v1/videos/{id}/content → <binary video/mp4>
```

Related: [[feedback-video-content-endpoint]] [[project-veo31-model]]
