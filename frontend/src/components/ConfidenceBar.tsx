export function ConfidenceBar({ score, threshold }: { score: number; threshold: number }) {
  return (
    <div>
      <div className="relative h-3 overflow-hidden rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500">
        <span className="absolute top-0 h-3 w-0.5 bg-slate-900 dark:bg-white" style={{ left: `${Math.max(0, Math.min(1, threshold)) * 100}%` }} title="Threshold" />
        <span className="absolute -top-1 h-5 w-1 rounded bg-slate-900 dark:bg-white" style={{ left: `calc(${Math.max(0, Math.min(1, score)) * 100}% - 2px)` }} />
      </div>
      <div className="mt-1 flex justify-between text-xs text-slate-500">
        <span>Authentic</span>
        <span>Manipulated</span>
      </div>
    </div>
  );
}
