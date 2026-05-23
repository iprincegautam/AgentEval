"use client";

import { useState } from "react";

export type EvalReport = {
  repo_url: string;
  overall_status: string;
  overall_score?: number;
  report: Record<string, unknown>;
};

type Props = {
  onReport: (report: EvalReport) => void;
  onError: (message: string) => void;
  onProgress: (message: string | null) => void;
};

export default function EvalForm({ onReport, onError, onProgress }: Props) {
  const [repoUrl, setRepoUrl] = useState(
    "https://github.com/open-gitagent/gitagent"
  );
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    onError("");
    onProgress("Fetching GitAgent files from GitHub…");

    try {
      onProgress("Running Rules, Identity, and Probe agents…");
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl.trim() }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || data.detail || "Evaluation failed");
      }

      onReport(data as EvalReport);
      onProgress(null);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unknown error");
      onProgress(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <label htmlFor="repo-url" style={{ display: "block", marginBottom: "0.5rem" }}>
        GitAgent repository URL
      </label>
      <input
        id="repo-url"
        type="url"
        placeholder="https://github.com/owner/repo"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        required
        disabled={loading}
      />
      <button className="primary" type="submit" disabled={loading}>
        {loading ? "Evaluating…" : "Run evaluation"}
      </button>
    </form>
  );
}
