import type { ReactNode } from "react";

export function Hero({ children }: { children: ReactNode }) {
  return (
    <section className="relative overflow-hidden px-5 pb-6 pt-10">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_top,#E0E7FF,transparent_60%)] dark:bg-[radial-gradient(circle_at_top,#312e81,transparent_55%)]" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[radial-gradient(#c7d2fe_1px,transparent_1px)] [background-size:18px_18px] opacity-50 [mask-image:linear-gradient(to_bottom,black,transparent)] dark:opacity-30" />
      <div className="relative mx-auto max-w-3xl text-center">
        <p className="inline-flex rounded-full border border-indigo-100 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#4F46E5] dark:border-indigo-900 dark:bg-slate-900/70">
          ELA + CNN image forensics
        </p>
        <h1 className="mt-4 bg-gradient-to-r from-slate-900 via-[#4F46E5] to-sky-500 bg-clip-text text-5xl font-semibold leading-[1.05] tracking-tight text-transparent sm:text-[60px] sm:leading-[64px] dark:from-white dark:via-indigo-200 dark:to-sky-300">
          Is this image real?
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-slate-500 dark:text-slate-300">
          Upload a photo. We re-save it, measure the differences, and score those differences with a small network.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2 text-sm text-slate-600 dark:text-slate-300">
          <span className="rounded-full bg-white px-3 py-1 shadow-sm dark:bg-slate-900">Runs locally</span>
          <span className="rounded-full bg-white px-3 py-1 shadow-sm dark:bg-slate-900">Nothing stored</span>
        </div>
        <div className="mt-8 text-left">{children}</div>
      </div>
    </section>
  );
}
