import type { ExperimentResult } from "../types";

const badgeClassName =
  "rounded-full border border-black/10 bg-sand px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-ink/70";

interface RetrievalInspectorProps {
  result?: ExperimentResult | null;
  title?: string;
}

export function RetrievalInspector({ result, title = "Retrieval Inspector" }: RetrievalInspectorProps) {
  if (!result) {
    return (
      <div className="rounded-[28px] border border-dashed border-black/15 bg-white/50 p-8 text-sm text-ink/60">
        Run an experiment to inspect retrieved chunks, prompt assembly, grounded answer generation, and evaluation.
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <p className="text-xs uppercase tracking-[0.3em] text-coral">{title}</p>
        <h3 className="mt-2 text-2xl font-semibold">{result.label || result.question}</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          <span className={badgeClassName}>Groundedness {result.evaluation.groundedness}</span>
          <span className={badgeClassName}>Relevance {result.evaluation.answer_relevance}</span>
          <span className={badgeClassName}>Coverage {result.evaluation.context_coverage}</span>
        </div>
        <p className="mt-4 rounded-2xl bg-sand p-4 text-sm leading-7">{result.generation.answer}</p>
        {result.evaluation.hallucination_flags.length ? (
          <div className="mt-4 rounded-2xl border border-coral/25 bg-coral/10 p-4 text-sm">
            <p className="font-semibold">Hallucination flags</p>
            <ul className="mt-2 space-y-2">
              {result.evaluation.hallucination_flags.map((flag) => (
                <li key={flag}>{flag}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <h4 className="text-lg font-semibold">Retrieved Chunks</h4>
        <div className="mt-4 grid gap-4">
          {result.retrieved_chunks.map((chunk) => (
            <article key={chunk.chunk_id} className="rounded-2xl border border-black/10 bg-sand p-4">
              <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.2em] text-ink/60">
                <span>Rank {chunk.rank}</span>
                <span>{chunk.citation}</span>
                <span>Vector {chunk.vector_score}</span>
                {chunk.rerank_score !== null && chunk.rerank_score !== undefined ? <span>Rerank {chunk.rerank_score}</span> : null}
              </div>
              <p className="mt-3 text-sm font-semibold">{chunk.document_name}</p>
              <p className="mt-2 text-sm leading-7 text-ink/80">{chunk.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <h4 className="text-lg font-semibold">Final Prompt</h4>
        <pre className="mt-4 overflow-x-auto rounded-2xl bg-ink p-4 text-xs leading-6 text-white">
          {result.generation.prompt}
        </pre>
      </section>
    </div>
  );
}
