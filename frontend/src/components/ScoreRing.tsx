import { useEffect, useState } from "react";

export function ScoreRing({ score }: { score: number }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(score);
      return;
    }
    const start = performance.now();
    let frame = 0;
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / 700);
      setShown(score * progress);
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [score]);
  const radius = 54;
  const circ = 2 * Math.PI * radius;
  return (
    <div className="relative grid h-36 w-36 place-items-center">
      <svg viewBox="0 0 140 140" className="h-36 w-36 -rotate-90" aria-hidden="true">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="currentColor" className="text-slate-200 dark:text-slate-700" strokeWidth="10" />
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#4F46E5" strokeWidth="10" strokeLinecap="round" strokeDasharray={`${circ * Math.max(0, Math.min(1, shown))} ${circ}`} />
      </svg>
      <div className="absolute text-center">
        <p className="font-mono text-2xl tabular-nums">{shown.toFixed(2)}</p>
        <p className="text-xs uppercase tracking-wide text-slate-500">Model score</p>
      </div>
    </div>
  );
}
