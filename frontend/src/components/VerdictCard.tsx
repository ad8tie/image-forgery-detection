import type { PredictResult } from "../lib/api";
import { ConfidenceBar } from "./ConfidenceBar";
import { ScoreRing } from "./ScoreRing";

const tones: Record<string, string> = {
  "Likely Authentic": "border-t-emerald-500 bg-gradient-to-b from-emerald-50 to-white dark:from-emerald-950 dark:to-slate-900",
  "Potentially Manipulated": "border-t-rose-500 bg-gradient-to-b from-rose-50 to-white dark:from-rose-950 dark:to-slate-900",
  "Not sure": "border-t-amber-500 bg-gradient-to-b from-amber-50 to-white dark:from-amber-950 dark:to-slate-900",
};

export function VerdictCard({
  result,
  onReset,
  onDownload,
  onCopy,
}: {
  result: PredictResult;
  onReset: () => void;
  onDownload: () => void;
  onCopy: () => void;
}) {
  const tone = tones[result.label] ?? tones["Not sure"];
  return (
    <article className={`rounded-[20px] border border-[#E2E8F0] border-t-4 p-6 shadow-[0_8px_30px_rgba(15,23,42,0.06)] dark:border-slate-700 ${tone}`}>
      <div className="flex items-start justify-between gap-3">
        <span className="rounded-full bg-white/80 px-3 py-1 text-sm font-semibold dark:bg-slate-900/70">{result.label}</span>
        {typeof result.inference_ms === "number" && (
          <span className="font-mono text-xs text-slate-500">{Math.round(result.inference_ms)} ms</span>
        )}
      </div>
      <div className="mt-4"><ScoreRing score={result.score} /></div>
      <p className="mt-3 text-slate-700 dark:text-slate-200">{result.explanation}</p>
      <div className="mt-4"><ConfidenceBar score={result.score} threshold={result.threshold} /></div>
      <div className="mt-5 flex flex-wrap gap-2">
        <button type="button" className="rounded-2xl bg-gradient-to-r from-[#4F46E5] to-sky-500 px-4 py-3 font-semibold text-white shadow-[0_8px_20px_rgba(79,70,229,0.35)]" onClick={onReset}>
          Check another image
        </button>
        <button type="button" className="rounded-2xl border border-[#E2E8F0] bg-white px-4 py-3 font-semibold dark:border-slate-700 dark:bg-slate-900" onClick={onDownload}>
          Download report
        </button>
        <button type="button" className="rounded-2xl px-4 py-3 font-semibold text-slate-600 dark:text-slate-300" onClick={onCopy}>
          Copy
        </button>
      </div>
    </article>
  );
}
