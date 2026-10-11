export function Histogram({ bins, mean }: { bins: number[]; mean: number }) {
  const peak = Math.max(...bins, 1);
  return (
    <article className="rounded-[20px] border border-[#E2E8F0] bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Error histogram</h2>
      <p className="mt-1 font-mono text-xs text-slate-500">Mean {mean.toFixed(1)}</p>
      <div className="mt-3 flex h-24 items-end gap-1" aria-label="16-bin error histogram">
        {bins.map((count, index) => (
          <div key={index} className="flex-1 rounded-t bg-[#4F46E5]" style={{ height: `${(count / peak) * 100}%` }} title={`${count}`} />
        ))}
      </div>
    </article>
  );
}
