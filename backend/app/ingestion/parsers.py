from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class UnsupportedDocumentError(ValueError):
    pass


class DocumentParser:
    SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}

    def parse(self, file_path: Path) -> tuple[str, dict]:
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_SUFFIXES:
            raise UnsupportedDocumentError(f"Unsupported file type: {suffix}")

        if suffix in {".txt", ".md", ".markdown"}:
            text = file_path.read_text(encoding="utf-8")
            return text, {"suffix": suffix, "character_count": len(text)}

        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages).strip()
        return text, {
            "suffix": suffix,
            "page_count": len(reader.pages),
            "character_count": len(text),
        }

    @staticmethod
    def content_type_for(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        return {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".markdown": "text/markdown",
            ".pdf": "application/pdf",
        }.get(suffix, "application/octet-stream")
