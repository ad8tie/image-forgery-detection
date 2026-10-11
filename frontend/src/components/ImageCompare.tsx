type Mode = "Original" | "Heatmap" | "Overlay";

export function ImageCompare({
  original,
  heatmap,
  mode,
}: {
  original: string;
  heatmap: string;
  mode: Mode;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-slate-100">
      {mode !== "Heatmap" && <img src={original} alt="Uploaded image" className="max-h-[420px] w-full object-contain" />}
      {heatmap && mode === "Heatmap" && <img src={heatmap} alt="Error level analysis map" className="max-h-[420px] w-full object-contain" />}
      {heatmap && mode === "Overlay" && (
        <img src={heatmap} alt="" className="absolute inset-0 max-h-[420px] w-full object-contain opacity-50" />
      )}
    </div>
  );
}
