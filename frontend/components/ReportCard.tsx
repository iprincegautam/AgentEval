"use client";
import { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface RulesResult {
  score: number;
  passed: boolean;
  summary: string;
  issues: string[];
  strengths: string[];
}

interface ProbeResult {
  top_risk: string;
  probes: { prompt: string; target_failure: string; failure_type: string; severity: string }[];
  coverage_gaps: string[];
}

interface IdentityResult {
  score: number;
  passed: boolean;
  identity_clarity: string;
  summary: string;
  issues: string[];
  strengths: string[];
}

interface FinalReport {
  overall_score: number;
  grade: string;
  verdict: string;
  executive_summary: string;
  top_3_issues: string[];
  top_3_strengths: string[];
  failure_taxonomy: Record<string, number>;
  recommendation: string;
}

interface EvalReport {
  repo: string;
  files_found: string[];
  rules_eval: RulesResult;
  probe_eval: ProbeResult;
  identity_eval: IdentityResult;
  final_report: FinalReport;
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function Shimmer({ className }: { className: string }) {
  return (
    <div className={`bg-zinc-800 rounded animate-pulse ${className}`} />
  );
}

function ReportCardSkeleton() {
  return (
    <div className="mt-8 space-y-6">
      {/* Header block */}
      <div className="border border-zinc-700 rounded-lg p-6 space-y-3">
        <div className="flex items-center justify-between">
          <Shimmer className="h-3 w-40" />
          <Shimmer className="h-10 w-10" />
        </div>
        <Shimmer className="h-5 w-32" />
        <Shimmer className="h-3 w-full" />
        <Shimmer className="h-3 w-3/4" />
      </div>

      {/* Taxonomy block */}
      <div className="border border-zinc-700 rounded-lg p-5">
        <Shimmer className="h-2 w-28 mb-5" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-2 flex flex-col items-center">
              <Shimmer className="h-7 w-10" />
              <Shimmer className="h-2 w-16" />
            </div>
          ))}
        </div>
      </div>

      {/* 3 agent cards */}
      <div className="grid grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border border-zinc-700 rounded-lg p-4 space-y-3">
            <Shimmer className="h-2 w-20" />
            <Shimmer className="h-7 w-16" />
            <Shimmer className="h-3 w-full" />
            <Shimmer className="h-3 w-5/6" />
            <Shimmer className="h-3 w-4/6" />
          </div>
        ))}
      </div>

      {/* Issues + strengths */}
      <div className="grid grid-cols-2 gap-4">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="border border-zinc-700 rounded-lg p-4 space-y-3">
            <Shimmer className="h-2 w-20 mb-1" />
            {[...Array(3)].map((_, j) => (
              <Shimmer key={j} className={`h-3 ${j === 1 ? "w-5/6" : "w-full"}`} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Grade colour ─────────────────────────────────────────────────────────────

const GRADE_COLOR: Record<string, string> = {
  A: "text-green-400",
  B: "text-lime-400",
  C: "text-yellow-400",
  D: "text-orange-400",
  F: "text-red-400",
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function AgentBlock({ title, score, summary, issues }: {
  title: string; score: number; summary: string; issues: string[];
}) {
  const color =
    score >= 70 ? "text-green-400" : score >= 40 ? "text-yellow-400" : "text-red-400";
  return (
    <div className="border border-zinc-700 rounded-lg p-4">
      <div className="text-xs text-zinc-500 mb-2">{title}</div>
      <div className={`text-2xl font-bold ${color} mb-2`}>{score}/100</div>
      <p className="text-xs text-zinc-400 mb-3 leading-relaxed">{summary}</p>
      {issues?.slice(0, 2).map((issue, idx) => (
        <div key={idx} className="text-xs text-zinc-500 border-l border-zinc-700 pl-2 mb-1 leading-relaxed">
          {issue}
        </div>
      ))}
    </div>
  );
}

function ProbeBlock({ probe }: { probe: ProbeResult }) {
  const severityColor: Record<string, string> = {
    critical: "text-red-400",
    high: "text-orange-400",
    medium: "text-yellow-400",
    low: "text-zinc-400",
  };
  return (
    <div className="border border-zinc-700 rounded-lg p-4">
      <div className="text-xs text-zinc-500 mb-2">Probe Agent</div>
      <div className="text-xs text-zinc-300 mb-3 font-semibold leading-relaxed">
        {probe.top_risk}
      </div>
      {probe.probes?.slice(0, 2).map((p, i) => (
        <div key={i} className="mb-2 border-l border-zinc-700 pl-2">
          <span className={`text-xs font-medium ${severityColor[p.severity] ?? "text-zinc-400"}`}>
            {p.severity}
          </span>
          <p className="text-xs text-zinc-500 mt-0.5 leading-relaxed">{p.target_failure}</p>
        </div>
      ))}
    </div>
  );
}

function IssueList({ title, items, color }: { title: string; items: string[]; color: string }) {
  return (
    <div className="border border-zinc-700 rounded-lg p-4">
      <div className="text-xs text-zinc-500 mb-3">{title}</div>
      {items?.map((item, i) => (
        <div key={i} className="flex gap-2 mb-2">
          <span className={`${color} shrink-0`}>→</span>
          <span className="text-xs text-zinc-300 leading-relaxed">{item}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Copy button ──────────────────────────────────────────────────────────────

function CopyButton({ data }: { data: EvalReport }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback for non-secure contexts
      const el = document.createElement("textarea");
      el.value = JSON.stringify(data, null, 2);
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={`text-xs px-3 py-1.5 rounded border transition-all duration-200 font-mono ${
        copied
          ? "border-green-400 text-green-400 bg-green-400/10"
          : "border-zinc-600 text-zinc-400 hover:border-zinc-400 hover:text-zinc-200"
      }`}
    >
      {copied ? "Copied!" : "{ } Copy JSON"}
    </button>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface ReportCardProps {
  data: EvalReport | null;
  loading: boolean;
}

export default function ReportCard({ data, loading }: ReportCardProps) {
  if (loading) return <ReportCardSkeleton />;
  if (!data) return null;

  const r = data.final_report;

  return (
    <div className="mt-8 space-y-6">
      {/* Header */}
      <div className="border border-zinc-700 rounded-lg p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="space-y-1">
            <span className="text-zinc-400 text-sm font-mono">{data.repo}</span>
            <div className="flex items-center gap-3 mt-1">
              <span
                className={`text-4xl font-bold ${GRADE_COLOR[r.grade] ?? "text-white"}`}
              >
                {r.grade}
              </span>
              <div>
                <div className="text-lg font-semibold text-white">{r.verdict}</div>
                <div className="text-xs text-zinc-500">Score: {r.overall_score}/100</div>
              </div>
            </div>
          </div>
          <CopyButton data={data} />
        </div>
        <p className="text-zinc-300 text-sm leading-relaxed mt-3">{r.executive_summary}</p>
        {r.recommendation && (
          <p className="text-xs text-zinc-500 mt-3 border-l-2 border-zinc-700 pl-3 italic">
            {r.recommendation}
          </p>
        )}
      </div>

      {/* Failure taxonomy */}
      <div className="border border-zinc-700 rounded-lg p-5">
        <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4">
          Failure Taxonomy
        </h2>
        <div className="grid grid-cols-4 gap-4 text-center">
          {Object.entries(r.failure_taxonomy).map(([k, v]) => (
            <div key={k}>
              <div className="text-2xl font-bold text-red-400">{v as number}</div>
              <div className="text-xs text-zinc-500 mt-1 leading-snug">
                {k.replace(/_/g, " ")}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3 agent results */}
      <div className="grid grid-cols-3 gap-4">
        <AgentBlock
          title="Rules Agent"
          score={data.rules_eval.score}
          summary={data.rules_eval.summary}
          issues={data.rules_eval.issues}
        />
        <AgentBlock
          title="Identity Agent"
          score={data.identity_eval.score}
          summary={data.identity_eval.summary}
          issues={data.identity_eval.issues}
        />
        <ProbeBlock probe={data.probe_eval} />
      </div>

      {/* Top issues + strengths */}
      <div className="grid grid-cols-2 gap-4">
        <IssueList title="Top Issues" items={r.top_3_issues} color="text-red-400" />
        <IssueList title="Strengths" items={r.top_3_strengths} color="text-green-400" />
      </div>

      {/* Files found */}
      <div className="border border-zinc-700 rounded p-4 flex flex-wrap items-center gap-2">
        <span className="text-xs text-zinc-500">Files parsed:</span>
        {data.files_found.map((f) => (
          <span
            key={f}
            className="text-xs bg-zinc-800 text-zinc-300 rounded px-2 py-1 font-mono"
          >
            {f}
          </span>
        ))}
      </div>
    </div>
  );
}
