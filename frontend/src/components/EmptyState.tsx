export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-[#E2E8F0] bg-white px-6 py-16 text-center">
      <h2 className="text-2xl font-semibold">{title}</h2>
      <p className="mx-auto mt-3 max-w-md text-[#64748B]">{body}</p>
    </div>
  );
}
