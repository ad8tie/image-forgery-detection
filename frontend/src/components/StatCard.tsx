export function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <article className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-[0_4px_24px_rgba(15,23,42,0.06)]" title={hint}>
      <p className="text-sm text-[#64748B]">{label}</p>
      <p className="mt-2 text-4xl font-semibold tracking-tight">{value}</p>
      <p className="mt-2 text-sm text-[#64748B]">{hint}</p>
    </article>
  );
}
