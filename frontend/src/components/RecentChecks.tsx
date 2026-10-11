export type RecentItem = {
  id: string;
  name: string;
  label: string;
  score: number;
  thumb: string;
};

const outline: Record<string, string> = {
  "Likely Authentic": "ring-emerald-400",
  "Potentially Manipulated": "ring-rose-400",
  "Not sure": "ring-amber-400",
};

export function RecentChecks({ items, onOpen }: { items: RecentItem[]; onOpen: (item: RecentItem) => void }) {
  if (!items.length) return null;
  return (
    <section className="mt-8">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Recent checks</h2>
      <div className="mt-3 flex gap-3 overflow-x-auto">
        {items.map((item) => (
          <button key={item.id} type="button" className={`w-24 shrink-0 text-left`} onClick={() => onOpen(item)}>
            <img src={item.thumb} alt="" className={`h-16 w-full rounded-xl object-cover ring-2 ${outline[item.label] ?? "ring-slate-300"}`} />
            <span className="mt-1 block truncate text-xs">{item.name}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
