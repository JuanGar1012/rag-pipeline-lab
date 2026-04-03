import type {
  ComparisonResult,
  ConfigOptions,
  DocumentDetail,
  DriftMonitorResponse,
  ExperimentResult,
  PipelineConfig
} from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listDocuments: () => request<DocumentDetail[]>("/documents"),
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<DocumentDetail>("/documents/upload", {
      method: "POST",
      body: formData
    });
  },
  listExperiments: () => request<ExperimentResult[]>("/experiments"),
  getConfigOptions: () => request<ConfigOptions>("/experiments/config/options"),
  runExperiment: (payload: {
    label?: string;
    question: string;
    document_ids: string[];
    config: PipelineConfig;
  }) =>
    request<ExperimentResult>("/experiments/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  compareExperiments: (payload: {
    label?: string;
    question: string;
    document_ids: string[];
    left: PipelineConfig;
    right: PipelineConfig;
  }) =>
    request<ComparisonResult>("/experiments/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  getDriftMonitor: () => request<DriftMonitorResponse>("/monitoring/drift")
};
