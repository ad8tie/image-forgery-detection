export function StepsTimeline({ quality, scale }: { quality: number; scale: number }) {
  const steps = [`JPEG quality ${quality}`, `ELA scale ${scale}`, "CNN scored the 128×128 map"];
  return (
    <article className="rounded-[20px] border border-[#E2E8F0] bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Steps</h2>
      <ol className="mt-4 space-y-3">
        {steps.map((step, index) => (
          <li key={step} className="flex gap-3">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-emerald-100 text-xs text-emerald-700">{index + 1}</span>
            <span className="text-sm">{step}</span>
          </li>
        ))}
      </ol>
    </article>
  );
}
