"use client";
import { useState } from "react";
import EvalForm from "@/components/EvalForm";
import ReportCard from "@/components/ReportCard";

export default function Home() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleEval(repoUrl: string) {
    setLoading(true);
    setError("");
    setResult(null);          // clear old report → skeleton shows immediately

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
        "http://localhost:8000";
      const res = await fetch(`${apiUrl}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? `Server error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Evaluation failed.";
      if (msg.includes("ANTHROPIC_API_KEY")) {
        setError(
          `${msg} — Create backend/.env with your key (see backend/.env.example), then restart uvicorn.`
        );
      } else if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        setError(
          `Cannot reach API — set NEXT_PUBLIC_API_URL or run backend: cd backend && uvicorn main:app --reload --port 8000`
        );
      } else {
        setError(msg || "Evaluation failed. Check the repo URL and try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  const showReport = loading || result !== null;

  return (
    <main className="min-h-screen bg-black text-white font-mono p-8">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight mb-1">
            AgentEval <span className="text-green-400">↯</span>
          </h1>
          <p className="text-zinc-400 text-sm">
            Paste a GitAgent repo. Get a structured quality report in seconds.
          </p>
          <p className="text-zinc-600 text-xs mt-1">
            Powered by RawEval Labs · 3-agent eval pipeline
          </p>
        </div>

        {/* Input */}
        <EvalForm onSubmit={handleEval} loading={loading} />

        {/* Error */}
        {error && (
          <div className="mt-4 px-4 py-3 border border-red-800 rounded bg-red-950/30 text-red-400 text-sm">
            {error}
          </div>
        )}

        {result?.demo && (
          <div className="mt-4 px-4 py-3 border border-yellow-800 rounded bg-yellow-950/30 text-yellow-300 text-sm">
            Demo mode — mock report (no ANTHROPIC_API_KEY). Add your key to{" "}
            <code className="text-yellow-200">backend/.env</code> for live Claude evals.
          </div>
        )}

        {/* Report / Skeleton */}
        {showReport && (
          <ReportCard data={result} loading={loading} />
        )}

      </div>
    </main>
  );
}
