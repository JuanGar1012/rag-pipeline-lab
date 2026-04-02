from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Iterable
from uuid import uuid4

from app.schemas import DocumentDetail, ExperimentResult
from app.storage.database import Database


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class DocumentRepository:
    def __init__(self, database: Database):
        self.database = database

    def list_documents(self) -> list[DocumentDetail]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM documents ORDER BY created_at DESC"
            ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def count_documents(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM documents").fetchone()
        return int(row["count"])

    def get_document(self, document_id: str) -> DocumentDetail | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
        return self._row_to_model(row) if row else None

    def get_documents(self, document_ids: Iterable[str]) -> list[DocumentDetail]:
        document_ids = list(document_ids)
        if not document_ids:
            return self.list_documents()
        placeholders = ",".join("?" for _ in document_ids)
        query = f"SELECT * FROM documents WHERE id IN ({placeholders}) ORDER BY created_at DESC"
        with self.database.connect() as connection:
            rows = connection.execute(query, tuple(document_ids)).fetchall()
        return [self._row_to_model(row) for row in rows]

    def create_document(
        self,
        *,
        filename: str,
        content_type: str,
        file_path: str,
        raw_text: str,
        metadata: dict,
    ) -> DocumentDetail:
        document = DocumentDetail(
            id=str(uuid4()),
            filename=filename,
            content_type=content_type,
            file_path=file_path,
            raw_text=raw_text,
            metadata=metadata,
            created_at=_utc_now(),
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (id, filename, content_type, file_path, raw_text, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.filename,
                    document.content_type,
                    document.file_path,
                    document.raw_text,
                    json.dumps(document.metadata),
                    document.created_at,
                ),
            )
            connection.commit()
        return document

    @staticmethod
    def _row_to_model(row) -> DocumentDetail:
        return DocumentDetail(
            id=row["id"],
            filename=row["filename"],
            content_type=row["content_type"],
            file_path=row["file_path"],
            raw_text=row["raw_text"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )


class ExperimentRepository:
    def __init__(self, database: Database):
        self.database = database

    def list_experiments(self) -> list[ExperimentResult]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT result_json FROM experiments ORDER BY created_at DESC"
            ).fetchall()
        return [ExperimentResult.model_validate_json(row["result_json"]) for row in rows]

    def get_experiment(self, experiment_id: str) -> ExperimentResult | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM experiments WHERE id = ?",
                (experiment_id,),
            ).fetchone()
        return ExperimentResult.model_validate_json(row["result_json"]) if row else None

    def save_experiment(
        self,
        *,
        label: str | None,
        question: str,
        config_json: str,
        result: ExperimentResult,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO experiments (id, label, question, config_json, result_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.id,
                    label,
                    question,
                    config_json,
                    result.model_dump_json(),
                    result.created_at,
                ),
            )
            connection.commit()
