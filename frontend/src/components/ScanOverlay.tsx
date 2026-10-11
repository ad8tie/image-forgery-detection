import { useEffect, useState } from "react";

const lines = ["Re-saving image...", "Computing error levels...", "Running the model..."];

export function ScanOverlay({ preview }: { preview: string }) {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setIndex((value) => (value + 1) % lines.length), 900);
    return () => window.clearInterval(timer);
  }, []);
  return (
    <div className="relative overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white dark:border-slate-800 dark:bg-slate-900">
      <img src={preview} alt="Image being analyzed" className="max-h-80 w-full object-contain" />
      <div className="scan-line pointer-events-none absolute inset-x-0 h-1 bg-[#4F46E5]/80 motion-reduce:hidden" />
      <p className="p-4 text-center text-sm font-medium text-slate-600 dark:text-slate-300" aria-live="polite">{lines[index]}</p>
    </div>
  );
}
