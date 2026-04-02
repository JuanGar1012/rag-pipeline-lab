from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from app.schemas import ChunkRecord


class FaissIndexStore:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def build(self, index_key: str, embeddings: list[list[float]], chunks: list[ChunkRecord]) -> None:
        index_path, metadata_path = self._paths(index_key)
        if index_path.exists() and metadata_path.exists():
            return

        matrix = np.asarray(embeddings, dtype="float32")
        if matrix.size == 0:
            raise ValueError("Cannot build an index with no embeddings.")
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, str(index_path))
        metadata_path.write_text(
            json.dumps([chunk.model_dump(mode="json") for chunk in chunks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def search(self, index_key: str, query_embedding: list[float], top_k: int) -> list[tuple[ChunkRecord, float]]:
        index_path, metadata_path = self._paths(index_key)
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f"Index {index_key} does not exist.")

        index = faiss.read_index(str(index_path))
        metadata = [
            ChunkRecord.model_validate(item)
            for item in json.loads(metadata_path.read_text(encoding="utf-8"))
        ]
        query = np.asarray([query_embedding], dtype="float32")
        faiss.normalize_L2(query)
        scores, indices = index.search(query, min(top_k, len(metadata)))

        matches: list[tuple[ChunkRecord, float]] = []
        for idx, score in zip(indices[0].tolist(), scores[0].tolist(), strict=False):
            if idx < 0:
                continue
            matches.append((metadata[idx], float(score)))
        return matches

    def _paths(self, index_key: str) -> tuple[Path, Path]:
        directory = self.root_dir / index_key
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "index.faiss", directory / "chunks.json"
