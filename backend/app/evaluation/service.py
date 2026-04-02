from __future__ import annotations

import re

from app.schemas import EvaluationResult, GenerationResult, RetrievedChunk


TOKEN_RE = re.compile(r"\b\w+\b")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


class EvaluationService:
    def evaluate(
        self,
        *,
        question: str,
        chunks: list[RetrievedChunk],
        generation: GenerationResult,
    ) -> EvaluationResult:
        context_text = " ".join(chunk.text for chunk in chunks)
        context_tokens = _tokens(context_text)
        question_tokens = _tokens(question)
        answer_tokens = _tokens(generation.answer)
        citations = set(generation.citations)

        groundedness = self._groundedness(generation.answer, context_tokens, citations)
        answer_relevance = self._jaccard(question_tokens, answer_tokens)
        context_coverage = self._context_coverage(answer_tokens, chunks)
        hallucination_flags = self._hallucination_flags(generation.answer, context_tokens, context_text, citations)

        summary = (
            "Strongly grounded response."
            if groundedness >= 0.7 and not hallucination_flags
            else "Response needs review for grounding gaps."
        )
        return EvaluationResult(
            groundedness=round(groundedness, 3),
            answer_relevance=round(answer_relevance, 3),
            context_coverage=round(context_coverage, 3),
            hallucination_flags=hallucination_flags,
            summary=summary,
        )

    def _groundedness(self, answer: str, context_tokens: set[str], citations: set[str]) -> float:
        sentences = [sentence.strip() for sentence in SENTENCE_RE.split(answer) if sentence.strip()]
        if not sentences:
            return 0.0
        scores = []
        for sentence in sentences:
            sentence_tokens = _tokens(sentence)
            overlap = self._jaccard(sentence_tokens, context_tokens)
            if any(citation in sentence for citation in citations):
                overlap = min(1.0, overlap + 0.15)
            scores.append(overlap)
        return sum(scores) / len(scores)

    def _context_coverage(self, answer_tokens: set[str], chunks: list[RetrievedChunk]) -> float:
        if not chunks:
            return 0.0
        covered = 0
        for chunk in chunks:
            if self._jaccard(answer_tokens, _tokens(chunk.text)) > 0.05:
                covered += 1
        return covered / len(chunks)

    def _hallucination_flags(
        self,
        answer: str,
        context_tokens: set[str],
        context_text: str,
        citations: set[str],
    ) -> list[str]:
        flags: list[str] = []
        sentences = [sentence.strip() for sentence in SENTENCE_RE.split(answer) if sentence.strip()]
        for sentence in sentences:
            overlap = self._jaccard(_tokens(sentence), context_tokens)
            if overlap < 0.08:
                flags.append(f"Low-context support: {sentence[:90]}")

        context_numbers = set(NUMBER_RE.findall(context_text))
        for number in NUMBER_RE.findall(answer):
            if number not in context_numbers:
                flags.append(f"Numeric claim not found in context: {number}")

        if not citations:
            flags.append("No inline citations detected in generated answer.")
        return flags[:5]

    @staticmethod
    def _jaccard(left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        union = left | right
        return len(left & right) / len(union)
