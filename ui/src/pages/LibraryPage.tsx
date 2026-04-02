import { useEffect, useState, type ChangeEvent } from "react";

import { Panel } from "../components/Panel";
import { api } from "../lib/api";
import { formatTimestamp } from "../lib/format";
import type { DocumentDetail } from "../types";

export function LibraryPage() {
  const [documents, setDocuments] = useState<DocumentDetail[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = async () => {
    try {
      setDocuments(await api.listDocuments());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load documents.");
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const onUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    try {
      setUploading(true);
      await api.uploadDocument(file);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  return (
    <div className="grid gap-6">
      <Panel
        eyebrow="Document Library"
        title="Ingest local documents and inspect metadata"
        action={
          <label className="cursor-pointer rounded-full bg-ink px-4 py-2 text-sm text-white">
            {uploading ? "Uploading..." : "Upload Document"}
            <input hidden type="file" accept=".txt,.md,.markdown,.pdf" onChange={onUpload} />
          </label>
        }
      >
        <p className="max-w-3xl text-sm leading-7 text-ink/75">
          Seed files load automatically on first boot. Add `.txt`, `.md`, or `.pdf` files to test ingestion,
          metadata tracking, and downstream retrieval experiments.
        </p>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </Panel>

      <div className="grid gap-4">
        {documents.map((document) => (
          <article key={document.id} className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold">{document.filename}</h3>
                <p className="text-sm text-ink/60">{document.content_type}</p>
              </div>
              <span className="rounded-full bg-sand px-3 py-1 text-xs uppercase tracking-[0.2em] text-ink/60">
                {formatTimestamp(document.created_at)}
              </span>
            </div>
            <div className="mt-4 grid gap-2 text-sm text-ink/75 md:grid-cols-3">
              <p>Path: {document.file_path}</p>
              <p>Chars: {String(document.metadata.character_count ?? "n/a")}</p>
              <p>Pages: {String(document.metadata.page_count ?? "n/a")}</p>
            </div>
            <p className="mt-4 line-clamp-4 text-sm leading-7 text-ink/80">{document.raw_text}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
