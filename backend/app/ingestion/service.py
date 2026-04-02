from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.ingestion.parsers import DocumentParser
from app.schemas import DocumentDetail
from app.storage.repositories import DocumentRepository


class IngestionService:
    def __init__(self, upload_dir: Path, repository: DocumentRepository, parser: DocumentParser):
        self.upload_dir = upload_dir
        self.repository = repository
        self.parser = parser
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def ingest_upload(self, upload: UploadFile) -> DocumentDetail:
        filename = upload.filename or "uploaded_document"
        destination = self.upload_dir / f"{uuid4()}_{filename}"
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        return self.ingest_file(destination, original_name=filename)

    def ingest_file(self, file_path: Path, original_name: str | None = None) -> DocumentDetail:
        text, metadata = self.parser.parse(file_path)
        return self.repository.create_document(
            filename=original_name or file_path.name,
            content_type=self.parser.content_type_for(file_path),
            file_path=str(file_path),
            raw_text=text,
            metadata=metadata,
        )

    def seed_directory(self, seed_dir: Path) -> list[DocumentDetail]:
        created: list[DocumentDetail] = []
        if not seed_dir.exists():
            return created
        for path in sorted(seed_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in self.parser.SUPPORTED_SUFFIXES:
                continue
            created.append(self.ingest_file(path, original_name=path.name))
        return created
