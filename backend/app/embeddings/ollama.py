from __future__ import annotations

import httpx


class OllamaEmbeddingClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def embed_texts(self, texts: list[str], model: str) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embed",
                json={"model": model, "input": texts},
            )
            if response.status_code == 404:
                vectors: list[list[float]] = []
                for text in texts:
                    legacy = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": model, "prompt": text},
                    )
                    legacy.raise_for_status()
                    vectors.append(legacy.json()["embedding"])
                return vectors

            response.raise_for_status()
            payload = response.json()
            return payload["embeddings"]
