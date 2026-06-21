---
name: feedback-image-editing-workaround
description: API易 /v1/images/edits returns 400; use /v1/chat/completions + base64 image_url for style transfer instead; MODEL_VIP is the right model for this
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## API易 image editing endpoint broken — use chat/completions instead

`POST /v1/images/edits` returns **400 Bad Request** on API易, even with correct parameters. The endpoint appears to be non-functional on this platform.

## Working alternative: /v1/chat/completions + image_url

Send the reference image as a **base64 data URL** in the chat `messages` array:

```python
import base64, requests

with open("reference.jpg", "rb") as f:
    raw = f.read()
b64 = base64.b64encode(raw).decode()

resp = requests.post(
    f"{BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-image-2-vip",  # MUST use vip or all (not official)
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                },
                {"type": "text", "text": "Redraw this as Ghibli anime style..."},
            ],
        }],
    },
    timeout=300,
)
```

## Image retrieval

The chat response includes a **CDN URL** in markdown format:

```
![image](https://files.chatgpt-topup.com/files/xxx.png)
```

Extract with regex, then download:
```python
import re
m = re.search(r"!\[.*?\]\((https?://[^\)]+)\)", content)
img_url = m.group(1)
time.sleep(2)  # brief CDN propagation delay
img_resp = requests.get(img_url)
```

**CDN download quirk:** Python's `urllib.request.urlretrieve()` returns 403 on the CDN (files.chatgpt-topup.com), but `requests.get()` returns 200. This is because the CDN checks User-Agent headers — `requests` sends a recognizable browser-like UA, while `urllib` sends `Python-urllib/3.x` which is blocked. Always use `requests` to download CDN images.

## Model choice

| Model | Chat endpoint? | Image input? | Best for |
|-------|---------------|-------------|----------|
| `gpt-image-2` (official) | No | No | Direct generation only |
| `gpt-image-2-vip` | Yes | Yes (base64) | **Style transfer** ★ |
| `gpt-image-2-all` | Yes | Yes (base64) | Also works |

## Style prompts that work well

- Studio Ghibli: "warm hand-drawn watercolor look, soft natural golden lighting, gentle pastels"
- Shinkai: "photorealistic backgrounds, dramatic lens flares, vibrant saturated skies"
- Ufotable: "sharp precise linework, dynamic lighting, ukiyo-e visual effects"
- Cyberpunk Edgerunners: "neon-drenched palette, high contrast cel shading, glitch effects"

Keep style prompts concise (~1-2 sentences, in English) to avoid content filter issues.

Related: [[feedback-size-param]] [[project-apiyi-models]]
