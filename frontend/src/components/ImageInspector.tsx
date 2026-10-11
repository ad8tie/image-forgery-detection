import { useState } from "react";
import type { PredictResult } from "../lib/api";

const modes = ["Original", "Heatmap", "Overlay"] as const;

export function ImageInspector({
  name,
  preview,
  result,
}: {
  name: string;
  preview: string;
  result: PredictResult;
}) {
  const [mode, setMode] = useState<(typeof modes)[number]>("Overlay");
  const [opacity, setOpacity] = useState(55);
  const [zoom, setZoom] = useState(false);
  const [hover, setHover] = useState<number | null>(null);
  const heatmap = result.ela_map_png_base64 ? `data:image/png;base64,${result.ela_map_png_base64}` : "";
  const showBoxes = mode === "Overlay" && result.regions.length > 0;

  const frame = (
    <div className="relative overflow-hidden rounded-2xl bg-slate-100 dark:bg-slate-800">
      {mode !== "Heatmap" && <img src={preview} alt={`Uploaded ${name}`} className="max-h-[420px] w-full object-contain" />}
      {heatmap && mode === "Heatmap" && <img src={heatmap} alt="Error level analysis map" className="max-h-[420px] w-full object-contain" />}
      {heatmap && mode === "Overlay" && (
        <img src={heatmap} alt="" className="pointer-events-none absolute inset-0 h-full w-full object-contain" style={{ opacity: opacity / 100 }} />
      )}
      {showBoxes &&
        result.regions.map((region, index) => (
          <button
            type="button"
            key={`${region.x}-${region.y}-${index}`}
            className={`absolute border-2 ${region.severity === "elevated" ? "border-dashed border-rose-500" : "border-amber-400"} ${hover === index ? "bg-white/20" : ""}`}
            style={{ left: `${region.x * 100}%`, top: `${region.y * 100}%`, width: `${region.w * 100}%`, height: `${region.h * 100}%` }}
            onMouseEnter={() => setHover(index)}
            onMouseLeave={() => setHover(null)}
            aria-label={`Region ${String.fromCharCode(65 + index)} ${region.severity}`}
          >
            <span className="absolute -top-5 left-0 whitespace-nowrap rounded bg-slate-900 px-1 text-[10px] text-white">
              Region {String.fromCharCode(65 + index)} · {region.severity}
            </span>
          </button>
        ))}
      <span className="absolute bottom-2 right-2 rounded bg-slate-900/80 px-2 py-1 text-[10px] uppercase tracking-wide text-white">Low → High</span>
    </div>
  );

  return (
    <article className="rounded-[20px] border border-[#E2E8F0] bg-white p-4 shadow-[0_8px_30px_rgba(15,23,42,0.06)] dark:border-slate-700 dark:bg-slate-900">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Inspection</p>
          <h2 className="font-semibold">{name}</h2>
          <p className="font-mono text-xs text-slate-500">
            {result.image_width}×{result.image_height} · {result.file_size_bytes} bytes
          </p>
        </div>
        <button type="button" className="rounded-xl border border-[#E2E8F0] px-3 py-1 text-sm dark:border-slate-700" onClick={() => setZoom(true)} aria-label="Open zoom lightbox">
          Zoom
        </button>
      </div>
      {frame}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {modes.map((item) => (
          <button key={item} type="button" className={`rounded-full px-3 py-1 text-sm ${mode === item ? "bg-[#4F46E5] text-white" : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-200"}`} onClick={() => setMode(item)}>
            {item}
          </button>
        ))}
        {mode === "Overlay" && (
          <label className="ml-auto text-xs text-slate-500">
            Opacity {opacity}%
            <input className="ml-2 align-middle accent-[#4F46E5]" type="range" min={20} max={90} value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} />
          </label>
        )}
      </div>
      {zoom && (
        <div className="fixed inset-0 z-40 grid place-items-center bg-slate-950/80 p-4" role="dialog" aria-modal="true" aria-label="Zoomed inspection">
          <button type="button" className="absolute right-4 top-4 text-white" onClick={() => setZoom(false)}>Close</button>
          <div className="max-h-[90vh] max-w-5xl">{frame}</div>
        </div>
      )}
    </article>
  );
}
