"use client";
import { useState } from "react";

interface EvalFormProps {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export default function EvalForm({ onSubmit, loading }: EvalFormProps) {
  const [url, setUrl] = useState("");

  return (
    <div className="flex gap-3">
      <style>{`
        @keyframes border-pulse {
          0%, 100% { border-color: rgb(74 222 128 / 0.4); box-shadow: 0 0 0 0 rgb(74 222 128 / 0); }
          50%       { border-color: rgb(74 222 128 / 0.9); box-shadow: 0 0 0 3px rgb(74 222 128 / 0.15); }
        }
        .input-loading { animation: border-pulse 2s ease-in-out infinite; }
      `}</style>
      <input
        className={`flex-1 bg-zinc-900 border rounded px-4 py-3 text-sm text-white placeholder-zinc-600 focus:outline-none transition-all duration-300 ${
          loading
            ? "border-green-400/40 input-loading"
            : "border-zinc-700 focus:border-green-400"
        }`}
        placeholder="https://github.com/owner/my-gitagent-repo"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={loading}
      />
      <button
        className="bg-green-400 text-black font-bold px-5 py-3 rounded text-sm hover:bg-green-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 min-w-[120px]"
        onClick={() => onSubmit(url)}
        disabled={loading || !url.trim()}
      >
        {loading ? (
          <span className="flex items-center gap-2 justify-center">
            <span className="w-3 h-3 border-2 border-black/40 border-t-black rounded-full animate-spin" />
            Evaluating
          </span>
        ) : (
          "Run Eval →"
        )}
      </button>
    </div>
  );
}
