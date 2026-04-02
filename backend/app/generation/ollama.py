from __future__ import annotations

import httpx


class OllamaGenerationClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str, model: str) -> str:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "stream": False,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You answer only from provided context and cite supporting chunks inline.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["message"]["content"].strip()
