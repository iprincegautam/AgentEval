"use client";

import { useState } from "react";
import EvalForm, { type EvalReport } from "@/components/EvalForm";
import ReportCard from "@/components/ReportCard";

export default function Home() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState<string | null>(null);

  return (
    <main>
      <h1>AgentEval</h1>
      <p className="subtitle">
        GitAgent quality evaluator — paste any GitAgent repo URL. We parse{" "}
        <code>agent.yaml</code>, <code>SOUL.md</code>, and <code>RULES.md</code>, then run
        three specialized eval agents and return a structured pass/fail report with failure
        taxonomy.
      </p>

      <EvalForm
        onReport={(r) => {
          setReport(r);
          setError("");
        }}
        onError={setError}
        onProgress={setProgress}
      />

      {progress && <p className="progress">{progress}</p>}
      {error && (
        <p className="card" style={{ color: "var(--fail)", borderColor: "var(--fail)" }}>
          {error}
        </p>
      )}
      {report && <ReportCard data={report} />}
    </main>
  );
}
