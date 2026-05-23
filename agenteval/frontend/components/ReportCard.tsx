"use client";

import type { EvalReport } from "./EvalForm";

type CheckResult = {
  status?: string;
  score?: number;
  summary?: string;
  findings?: Array<{ severity?: string; message?: string; taxonomy?: string }>;
  probes?: Array<{ prompt?: string; attack_type?: string; definition_supports_refusal?: boolean }>;
};

type Props = {
  data: EvalReport;
};

function StatusBadge({ status }: { status: string }) {
  const cls = status === "pass" ? "pass" : status === "warn" ? "warn" : "fail";
  return <span className={`badge ${cls}`}>{status}</span>;
}

function CheckCard({ title, check }: { title: string; check: CheckResult }) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{title}</strong>
        {check.status && <StatusBadge status={check.status} />}
      </div>
      {typeof check.score === "number" && (
        <p style={{ color: "var(--muted)", margin: "0.5rem 0" }}>Score: {check.score}/100</p>
      )}
      {check.summary && <p style={{ fontSize: "0.9rem", lineHeight: 1.5 }}>{check.summary}</p>}
      {check.findings && check.findings.length > 0 && (
        <ul style={{ paddingLeft: "1.2rem", margin: "0.5rem 0 0", fontSize: "0.85rem" }}>
          {check.findings.slice(0, 3).map((f, i) => (
            <li key={i}>{f.message}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function ReportCard({ data }: Props) {
  const report = data.report as Record<string, unknown>;
  const checks = (report.checks || {}) as Record<string, CheckResult>;
  const taxonomy = (report.failure_taxonomy || []) as Array<{
    code: string;
    severity: string;
    message: string;
    source?: string;
  }>;

  return (
    <section>
      <div className="card">
        <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
          <h2 style={{ margin: 0, fontSize: "1.25rem" }}>Evaluation report</h2>
          <StatusBadge status={data.overall_status} />
          {typeof data.overall_score === "number" && (
            <span style={{ color: "var(--muted)" }}>Overall: {data.overall_score}/100</span>
          )}
        </div>
        {Boolean(report.agent_name) && (
          <p style={{ color: "var(--muted)", margin: "0.5rem 0 0" }}>
            Agent: {String(report.agent_name)} v{String(report.agent_version)} · path:{" "}
            {String(report.agent_path)}
          </p>
        )}
        {Boolean(report.summary) && (
          <p style={{ marginTop: "1rem", lineHeight: 1.6 }}>{String(report.summary)}</p>
        )}
        {Boolean(report.error) && (
          <p style={{ color: "var(--fail)", marginTop: "1rem" }}>{String(report.error)}</p>
        )}
      </div>

      {checks.rules && (
        <div className="check-grid">
          <CheckCard title="Rules Agent" check={checks.rules} />
          {checks.identity && <CheckCard title="Identity Agent" check={checks.identity} />}
          {checks.probes && <CheckCard title="Probe Agent" check={checks.probes} />}
        </div>
      )}

      {taxonomy.length > 0 && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h3 style={{ marginTop: 0 }}>Failure taxonomy</h3>
          {taxonomy.map((item, i) => (
            <div
              key={i}
              className={`taxonomy-item ${item.severity === "medium" || item.severity === "low" ? "medium" : ""}`}
            >
              <strong>{item.code}</strong>
              <span style={{ color: "var(--muted)", marginLeft: "0.5rem" }}>
                [{item.severity}]
                {item.source ? ` · ${item.source}` : ""}
              </span>
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.9rem" }}>{item.message}</p>
            </div>
          ))}
        </div>
      )}

      {checks.probes?.probes && checks.probes.probes.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Adversarial probes</h3>
          {checks.probes.probes.map((p, i) => (
            <div key={i} style={{ marginBottom: "0.75rem", fontSize: "0.9rem" }}>
              <span className="badge warn" style={{ marginRight: "0.5rem" }}>
                {p.attack_type || "probe"}
              </span>
              <em>{p.prompt}</em>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
