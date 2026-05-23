import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentEval — GitAgent Quality Evaluator",
  description:
    "Evaluate any GitAgent repo: parse agent.yaml, SOUL.md, RULES.md and run multi-agent quality checks.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
