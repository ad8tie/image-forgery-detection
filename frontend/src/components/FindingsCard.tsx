import type { PredictResult } from "../lib/api";

export function FindingsCard({ result }: { result: PredictResult }) {
  const items: { ok: boolean; text: string }[] = [];
  const uniform = result.ela_stats?.uniform_area_pct;
  if (typeof uniform === "number") {
    items.push({
      ok: uniform >= 70,
      text: `${uniform.toFixed(0)}% of the error map stays under the even-compression cutoff.`,
    });
  }
  if (Array.isArray(result.regions)) {
    items.push({
      ok: result.regions.length === 0,
      text: result.regions.length === 0 ? "No hotspot region crossed the error cutoff." : `${result.regions.length} hotspot region${result.regions.length === 1 ? "" : "s"} crossed the error cutoff.`,
    });
  }
  const mean = result.ela_stats?.mean_error;
  const max = result.ela_stats?.max_error;
  if (typeof mean === "number" && typeof max === "number" && mean > 0 && max >= mean * 3) {
    items.push({ ok: false, text: `Peak error is ${max.toFixed(0)}, about ${(max / mean).toFixed(1)} times the average.` });
  }
  if (!items.length) return null;
  return (
    <article className="rounded-[20px] border border-[#E2E8F0] bg-white p-5 shadow-[0_8px_30px_rgba(15,23,42,0.06)] dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">What we found</h2>
      <ul className="mt-3 space-y-2">
        {items.slice(0, 3).map((item) => (
          <li key={item.text} className="text-sm text-slate-700 dark:text-slate-200">
            <span className={item.ok ? "text-emerald-600" : "text-amber-600"}>{item.ok ? "✓" : "!"} </span>
            {item.text}
          </li>
        ))}
      </ul>
    </article>
  );
}
