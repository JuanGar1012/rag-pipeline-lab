from __future__ import annotations

from collections import defaultdict

import numpy as np

from app.embeddings.base import EmbeddingClient
from app.schemas import DriftMonitorResponse, DriftPoint, DriftReport, DriftStatus, ExperimentResult


class DriftMonitoringService:
    def __init__(self, embedding_client: EmbeddingClient, embedding_model: str, baseline_window: int = 3):
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        self.baseline_window = baseline_window

    async def analyze(self, experiments: list[ExperimentResult]) -> DriftMonitorResponse:
        groups = self._group_by_family(experiments)
        reports: list[DriftReport] = []

        for family, runs in groups.items():
            if len(runs) < 2:
                continue
            runs.sort(key=lambda run: run.created_at)
            answer_embeddings = await self.embedding_client.embed_texts(
                [run.generation.answer for run in runs],
                self.embedding_model,
            )
            question_embeddings = await self.embedding_client.embed_texts(
                [run.question for run in runs],
                self.embedding_model,
            )
            reports.append(self._build_report(family, runs, answer_embeddings, question_embeddings))

        severity = {
            DriftStatus.ALERT: 2,
            DriftStatus.WATCH: 1,
            DriftStatus.HEALTHY: 0,
        }
        reports.sort(key=lambda report: (severity[report.status], report.latest_created_at), reverse=True)
        return DriftMonitorResponse(
            recommendation=(
                "Monitor semantic drift against a rolling baseline per experiment family, "
                "and require grounding metrics to stay stable before promoting a prompt or model change."
            ),
            reports=reports,
        )

    def _build_report(
        self,
        family: str,
        runs: list[ExperimentResult],
        answer_embeddings: list[list[float]],
        question_embeddings: list[list[float]],
    ) -> DriftReport:
        answer_vectors = [self._normalize(vector) for vector in answer_embeddings]
        question_vectors = [self._normalize(vector) for vector in question_embeddings]

        series: list[DriftPoint] = []
        for index in range(1, len(runs)):
            baseline_start = max(0, index - self.baseline_window)
            baseline_runs = runs[baseline_start:index]
            baseline_answers = answer_vectors[baseline_start:index]
            baseline_centroid = self._normalize(np.mean(baseline_answers, axis=0))

            current_run = runs[index]
            current_answer = answer_vectors[index]
            current_question = question_vectors[index]

            semantic_drift = max(0.0, 1 - self._cosine(current_answer, baseline_centroid))
            question_alignment = max(0.0, self._cosine(current_answer, current_question))
            grounding_baseline = sum(run.evaluation.groundedness for run in baseline_runs) / len(baseline_runs)
            grounding_drop = max(0.0, grounding_baseline - current_run.evaluation.groundedness)
            citation_density = len(current_run.generation.citations) / max(1, len(current_run.retrieved_chunks))
            retrieval_overlap = self._retrieval_overlap(current_run, baseline_runs)
            hallucination_count = len(current_run.evaluation.hallucination_flags)
            alerts = self._point_alerts(
                semantic_drift=semantic_drift,
                question_alignment=question_alignment,
                grounding_drop=grounding_drop,
                citation_density=citation_density,
                retrieval_overlap=retrieval_overlap,
                hallucination_count=hallucination_count,
            )
            series.append(
                DriftPoint(
                    experiment_id=current_run.id,
                    created_at=current_run.created_at,
                    semantic_drift=round(semantic_drift, 3),
                    question_alignment=round(question_alignment, 3),
                    grounding_drop=round(grounding_drop, 3),
                    citation_density=round(citation_density, 3),
                    retrieval_overlap=round(retrieval_overlap, 3),
                    hallucination_count=hallucination_count,
                    status=self._status_for_alerts(alerts),
                )
            )

        latest = runs[-1]
        latest_point = series[-1]
        alerts = self._point_alerts(
            semantic_drift=latest_point.semantic_drift,
            question_alignment=latest_point.question_alignment,
            grounding_drop=latest_point.grounding_drop,
            citation_density=latest_point.citation_density,
            retrieval_overlap=latest_point.retrieval_overlap,
            hallucination_count=latest_point.hallucination_count,
        )
        summary = self._summary(latest_point, alerts)
        return DriftReport(
            family=family,
            run_count=len(runs),
            latest_question=latest.question,
            latest_experiment_id=latest.id,
            latest_created_at=latest.created_at,
            status=latest_point.status,
            alerts=alerts,
            summary=summary,
            series=series,
        )

    @staticmethod
    def _group_by_family(experiments: list[ExperimentResult]) -> dict[str, list[ExperimentResult]]:
        groups: dict[str, list[ExperimentResult]] = defaultdict(list)
        for experiment in experiments:
            family = (experiment.label or experiment.question).strip() or "Unlabeled"
            groups[family].append(experiment)
        return groups

    @staticmethod
    def _retrieval_overlap(current_run: ExperimentResult, baseline_runs: list[ExperimentResult]) -> float:
        current = {chunk.citation for chunk in current_run.retrieved_chunks}
        baseline = {chunk.citation for run in baseline_runs for chunk in run.retrieved_chunks}
        if not current or not baseline:
            return 0.0
        return len(current & baseline) / len(current | baseline)

    @staticmethod
    def _point_alerts(
        *,
        semantic_drift: float,
        question_alignment: float,
        grounding_drop: float,
        citation_density: float,
        retrieval_overlap: float,
        hallucination_count: int,
    ) -> list[str]:
        alerts: list[str] = []
        if semantic_drift > 0.18:
            alerts.append(f"Semantic drift is elevated ({semantic_drift:.3f}).")
        if question_alignment < 0.55:
            alerts.append(f"Answer/question alignment is low ({question_alignment:.3f}).")
        if grounding_drop > 0.12:
            alerts.append(f"Groundedness fell versus baseline ({grounding_drop:.3f}).")
        if citation_density < 0.4:
            alerts.append(f"Citation density is thin ({citation_density:.3f}).")
        if retrieval_overlap < 0.15:
            alerts.append(f"Retrieved evidence changed sharply ({retrieval_overlap:.3f} overlap).")
        if hallucination_count > 0:
            alerts.append(f"{hallucination_count} hallucination flag(s) detected.")
        return alerts

    @staticmethod
    def _status_for_alerts(alerts: list[str]) -> DriftStatus:
        if len(alerts) >= 3:
            return DriftStatus.ALERT
        if alerts:
            return DriftStatus.WATCH
        return DriftStatus.HEALTHY

    @staticmethod
    def _summary(point: DriftPoint, alerts: list[str]) -> str:
        if not alerts:
            return "Latest run remains close to its recent semantic and grounding baseline."
        return (
            f"Latest run shows drift={point.semantic_drift:.3f}, alignment={point.question_alignment:.3f}, "
            f"grounding_drop={point.grounding_drop:.3f}."
        )

    @staticmethod
    def _normalize(vector: list[float] | np.ndarray) -> np.ndarray:
        array = np.asarray(vector, dtype="float32")
        norm = np.linalg.norm(array)
        return array if norm == 0 else array / norm

    @staticmethod
    def _cosine(left: np.ndarray, right: np.ndarray) -> float:
        return float(np.dot(left, right))
