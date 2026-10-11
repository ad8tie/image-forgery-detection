import { useState, type ReactNode } from "react";

export function Accordion({ title, children }: { title: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white">
      <button
        type="button"
        className="flex w-full items-center justify-between px-6 py-4 text-left text-base font-semibold"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {title}
        <span className="text-[#64748B]">{open ? "−" : "+"}</span>
      </button>
      {open && <div className="border-t border-[#E2E8F0] px-6 py-4 text-[#334155]">{children}</div>}
    </div>
  );
}
