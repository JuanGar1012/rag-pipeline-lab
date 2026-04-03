import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ComparePage } from "./pages/ComparePage";
import { ExperimentPage } from "./pages/ExperimentPage";
import { HistoryPage } from "./pages/HistoryPage";
import { LibraryPage } from "./pages/LibraryPage";
import { MonitorPage } from "./pages/MonitorPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<LibraryPage />} />
        <Route path="/experiment" element={<ExperimentPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/monitor" element={<MonitorPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
