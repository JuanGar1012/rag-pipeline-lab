import type { DocumentDetail } from "../types";

interface DocumentPickerProps {
  documents: DocumentDetail[];
  selectedIds: string[];
  onChange: (next: string[]) => void;
}

export function DocumentPicker({ documents, selectedIds, onChange }: DocumentPickerProps) {
  const toggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((value) => value !== id));
      return;
    }
    onChange([...selectedIds, id]);
  };

  return (
    <div className="grid gap-3">
      {documents.map((document) => {
        const selected = selectedIds.includes(document.id);
        return (
          <button
            key={document.id}
            type="button"
            onClick={() => toggle(document.id)}
            className={`rounded-2xl border px-4 py-3 text-left transition ${
              selected ? "border-ink bg-ink text-white" : "border-black/10 bg-sand hover:border-coral"
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-medium">{document.filename}</p>
                <p className={`text-xs ${selected ? "text-white/70" : "text-ink/60"}`}>{document.content_type}</p>
              </div>
              <div className={`h-4 w-4 rounded-full border ${selected ? "border-white bg-coral" : "border-ink/20"}`} />
            </div>
          </button>
        );
      })}
      {!documents.length ? <p className="text-sm text-ink/60">No documents available yet.</p> : null}
    </div>
  );
}
