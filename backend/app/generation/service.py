from __future__ import annotations

import re
from typing import Protocol

from app.schemas import GenerationResult, RetrievedChunk


class GenerationClient(Protocol):
    async def generate(self, prompt: str, model: str) -> str:
        ...


class GenerationService:
    def __init__(self, client: GenerationClient, default_generation_model: str):
        self.client = client
        self.default_generation_model = default_generation_model

    async def grounded_answer(
        self,
        *,
        question: str,
        chunks: list[RetrievedChunk],
        model: str | None,
    ) -> GenerationResult:
        prompt = self.build_prompt(question, chunks)
        answer = await self.client.generate(prompt, model or self.default_generation_model)
        citations = [chunk.citation for chunk in chunks if chunk.citation in answer]
        if not citations:
            citations = [chunk.citation for chunk in chunks[:2]]
        return GenerationResult(prompt=prompt, answer=answer, citations=citations)

    @staticmethod
    def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
        context_lines = []
        for chunk in chunks:
            context_lines.append(
                f"{chunk.citation} | source={chunk.document_name} | score={chunk.vector_score:.4f}\n{chunk.text}"
            )
        context = "\n\n".join(context_lines)
        return (
            "You are running inside RAG Pipeline Lab.\n"
            "Answer the user question using only the provided context.\n"
            "Rules:\n"
            "- Be explicit when context is incomplete.\n"
            "- Cite supporting chunks inline using the provided bracketed ids.\n"
            "- Prefer concise, evidence-backed statements.\n\n"
            f"Question:\n{question}\n\n"
            f"Context:\n{context}\n\n"
            "Final answer:"
        )

    @staticmethod
    def extract_citations(answer: str) -> list[str]:
        return re.findall(r"\[[^\]]+\]", answer)
