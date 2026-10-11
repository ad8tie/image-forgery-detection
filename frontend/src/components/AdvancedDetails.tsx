import { useState } from "react";

export function AdvancedDetails({
  quality,
  scale,
  sha,
  threshold,
  onQuality,
  onScale,
  onRerun,
}: {
  quality: number;
  scale: number;
  sha: string;
  threshold: number;
  onQuality: (value: number) => void;
  onScale: (value: number) => void;
  onRerun: () => void;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <article className="rounded-[20px] border border-[#E2E8F0] bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Advanced details</h2>
      <label className="mt-3 block text-sm">
        JPEG quality {quality}
        <input className="mt-1 w-full accent-[#4F46E5]" type="range" min={50} max={100} value={quality} onChange={(event) => onQuality(Number(event.target.value))} />
      </label>
      <label className="mt-3 block text-sm">
        ELA scale {scale}
        <input className="mt-1 w-full accent-[#4F46E5]" type="range" min={1} max={30} value={scale} onChange={(event) => onScale(Number(event.target.value))} />
      </label>
      <button type="button" className="mt-3 rounded-2xl bg-[#4F46E5] px-4 py-2 text-sm font-semibold text-white" onClick={onRerun}>Re-run</button>
      <p className="mt-3 font-mono text-xs text-slate-500">Threshold {threshold.toFixed(2)}</p>
      {sha && (
        <button
          type="button"
          className="mt-2 block break-all text-left font-mono text-xs text-slate-500"
          onClick={async () => {
            await navigator.clipboard.writeText(sha);
            setCopied(true);
          }}
        >
          SHA-256 {sha} {copied ? "Copied" : "Copy"}
        </button>
      )}
    </article>
  );
}
