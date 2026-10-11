import { useState } from "react";
import { NavLink } from "react-router-dom";
import { APP_NAME } from "../lib/config";
import { useTheme } from "../lib/theme";

const links = [
  { to: "/", label: "Check Image", end: true },
  { to: "/how-it-works", label: "How It Works", end: false },
  { to: "/results", label: "Model Results", end: false },
];

export function Navbar({ online }: { online: boolean | null }) {
  const { dark, toggle } = useTheme();
  const [open, setOpen] = useState(false);
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-[#E2E8F0] bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <div className="mx-auto flex max-w-[1100px] items-center justify-between gap-3 px-5 py-3">
        <NavLink to="/" className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
          <span className="grid h-9 w-9 place-items-center rounded-2xl bg-[#4F46E5] text-sm text-white">AI</span>
          <span>{APP_NAME}</span>
        </NavLink>
        <button type="button" className="rounded-xl px-3 py-2 text-sm md:hidden" aria-label="Open menu" onClick={() => setOpen((value) => !value)}>
          Menu
        </button>
        <nav className={`${open ? "flex" : "hidden"} absolute left-0 right-0 top-full flex-col gap-2 border-b border-[#E2E8F0] bg-white p-4 dark:border-slate-800 dark:bg-slate-950 md:static md:flex md:flex-row md:items-center md:border-0 md:bg-transparent md:p-0`}>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `rounded-xl px-3 py-2 text-sm ${isActive ? "font-semibold text-[#4F46E5]" : "text-slate-500 dark:text-slate-300"}`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${online ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300"}`}>
            <span className={`h-2 w-2 rounded-full ${online ? "bg-[#10B981]" : "bg-slate-400"}`} />
            {online ? "Backend online" : "Offline"}
          </span>
          <button type="button" className="rounded-xl px-3 py-2 text-sm" aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} onClick={toggle}>
            {dark ? "Light" : "Dark"}
          </button>
        </nav>
      </div>
    </header>
  );
}
