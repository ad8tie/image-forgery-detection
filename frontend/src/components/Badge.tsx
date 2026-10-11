const tones = {
  green: "bg-emerald-50 text-[#059669]",
  red: "bg-red-50 text-[#DC2626]",
  amber: "bg-amber-50 text-[#B45309]",
  grey: "bg-slate-100 text-[#64748B]",
};

export function Badge({ tone, children }: { tone: keyof typeof tones; children: string }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${tones[tone]}`}>{children}</span>;
}
