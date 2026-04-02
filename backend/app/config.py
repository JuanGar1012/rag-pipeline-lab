from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Pipeline Lab"
    api_prefix: str = "/api"
    environment: str = "development"
    storage_root: Path = Path(__file__).resolve().parents[1] / "data"
    upload_dir: Path = storage_root / "uploads"
    index_dir: Path = storage_root / "indexes"
    sqlite_path: Path = storage_root / "rag_lab.db"
    seed_docs_dir: Path = Path(__file__).resolve().parent / "seed_docs"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    auto_seed: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.index_dir.mkdir(parents=True, exist_ok=True)
    return settings
