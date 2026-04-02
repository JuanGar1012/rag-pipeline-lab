from app.chunking.strategies import ChunkingService
from app.schemas import ChunkStrategy, DocumentDetail, PipelineConfig


def test_overlap_chunking_creates_multiple_windows():
    service = ChunkingService()
    document = DocumentDetail(
        id="doc-1",
        filename="demo.txt",
        content_type="text/plain",
        file_path="demo.txt",
        raw_text=" ".join(f"token{i}" for i in range(220)),
        metadata={},
        created_at="2026-01-01T00:00:00Z",
    )

    chunks = service.chunk_documents(
        [document],
        PipelineConfig(chunk_strategy=ChunkStrategy.OVERLAP, chunk_size=80, overlap=20),
    )

    assert len(chunks) == 4
    assert chunks[1].text.startswith("token60")
