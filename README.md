# RAG Pipeline Lab

RAG Pipeline Lab is a local-first experimentation platform for retrieval-augmented generation. It lets you upload documents, vary chunking and retrieval settings, inspect retrieved evidence, compare pipeline configurations side by side, and score answer quality with lightweight grounding heuristics.

## Stack

- Backend: FastAPI, Pydantic, SQLite, FAISS, Ollama
- Frontend: React, Vite, Tailwind
- Retrieval: local embeddings, local vector index, optional reranking
- Generation: grounded prompt assembly with chunk citations
- Evaluation: groundedness, answer relevance, context coverage, hallucination flags

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- chunking/
|   |   |-- embeddings/
|   |   |-- evaluation/
|   |   |-- generation/
|   |   |-- indexing/
|   |   |-- ingestion/
|   |   |-- retrieval/
|   |   |-- seed_docs/
|   |   |-- storage/
|   |   |-- tests/
|   |   |-- config.py
|   |   |-- main.py
|   |   |-- pipeline.py
|   |   `-- schemas.py
|   `-- pyproject.toml
|-- ui/
|   |-- src/
|   |   |-- components/
|   |   |-- lib/
|   |   |-- pages/
|   |   `-- types/
|   |-- package.json
|   `-- tailwind.config.ts
|-- docker-compose.yml
`-- .env.example
```

## Features

- Document ingestion for `.txt`, `.md`, `.markdown`, and `.pdf`
- Metadata tracking and auto-seeded example docs
- Fixed, overlap, and paragraph-aware semantic-style chunking
- Configurable chunk size, overlap, top-k, embedding model, generation model, and reranking
- Retrieval inspector with chunk scores, source docs, prompt view, final answer, and citations
- Answer evaluation with heuristic scoring
- Side-by-side comparison of two pipeline configurations
- Drift monitoring over experiment logs using semantic and grounding signals
- Experiment history persisted in SQLite

## Backend Design

The backend keeps retrieval and generation separate:

- `ingestion/` parses files and stores canonical raw text.
- `chunking/` produces experiment-specific chunks from stored documents.
- `embeddings/` calls Ollama for local embeddings.
- `indexing/` persists FAISS indexes keyed by pipeline configuration.
- `retrieval/` handles vector search and optional lexical reranking.
- `generation/` builds a grounded prompt and calls Ollama chat.
- `evaluation/` scores the answer against retrieved context.
- `storage/` owns SQLite initialization and repositories.

This makes it easy to swap chunkers, embedders, rerankers, or generators without rewriting the API layer.

## API Surface

- `GET /api/health`
- `GET /api/documents`
- `POST /api/documents/upload`
- `GET /api/documents/{document_id}`
- `GET /api/experiments`
- `GET /api/experiments/config/options`
- `POST /api/experiments/run`
- `POST /api/experiments/compare`
- `GET /api/experiments/{experiment_id}`
- `GET /api/monitoring/drift`

## Local Setup

### 1. Start Ollama and pull models

```bash
ollama serve
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
copy ..\.env.example .env
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd ui
npm install
npm run dev
```

The UI runs at `http://localhost:5173` and the API runs at `http://localhost:8000`.

## Docker

You can run the full stack with Docker Compose:

```bash
docker compose up --build
```

This starts:

- FastAPI on `http://localhost:8000`
- React UI on `http://localhost:4173`
- Ollama on `http://localhost:11434`

## Evaluation Notes

The evaluation service uses transparent heuristics rather than hidden judge-model scoring:

- Groundedness: token overlap between answer sentences and retrieved context, with citation bonus
- Answer relevance: overlap between question tokens and answer tokens
- Context coverage: how many retrieved chunks materially contribute to the answer
- Hallucination flags: low-support sentences, unmatched numeric claims, and missing citations

These heuristics are intentionally simple so they can be inspected, tuned, and replaced.

## Seed Data

On first startup the app ingests sample docs from [backend/app/seed_docs](/C:/Users/juang/Dev/projects/Codex/rag-pipeline-lab/backend/app/seed_docs) so the UI is immediately usable.

## Tests

Backend tests cover:

- overlap chunking behavior
- evaluation warnings for missing citations
- prompt/generation citation extraction

Run them with:

```bash
cd backend
pytest
```

## Portfolio Signal

This project is designed to show practical AI engineering discipline:

- retrieval tuning as a first-class workflow
- explainable inspection of context and prompts
- clear separation between retrieval and generation
- local-first stack choices for reproducible experimentation
- typed interfaces that support component swapping
