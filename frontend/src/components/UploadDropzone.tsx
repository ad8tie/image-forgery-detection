import { useEffect, type DragEvent, type ReactNode } from "react";

export function UploadDropzone({
  onFile,
  compact = false,
  samples,
}: {
  onFile: (file: File) => void;
  compact?: boolean;
  samples?: ReactNode;
}) {
  useEffect(() => {
    const onPaste = (event: ClipboardEvent) => {
      const file = Array.from(event.clipboardData?.files ?? []).find((item) => item.type.startsWith("image/"));
      if (file) onFile(file);
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, [onFile]);

  function take(list: FileList | null) {
    const file = list?.[0];
    if (file) onFile(file);
  }

  function onDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    event.currentTarget.classList.remove("border-[#4F46E5]", "bg-indigo-50");
    take(event.dataTransfer.files);
  }

  return (
    <div>
      <label
        className={`grid cursor-pointer place-items-center rounded-[20px] border border-dashed border-indigo-300 bg-white text-center shadow-[0_8px_30px_rgba(15,23,42,0.06)] transition hover:-translate-y-0.5 hover:border-[#4F46E5] dark:border-indigo-700 dark:bg-slate-900 ${compact ? "px-4 py-6" : "px-6 py-14"}`}
        onDragOver={(event) => {
          event.preventDefault();
          event.currentTarget.classList.add("border-[#4F46E5]", "bg-indigo-50");
        }}
        onDragLeave={(event) => event.currentTarget.classList.remove("border-[#4F46E5]", "bg-indigo-50")}
        onDrop={onDrop}
      >
        <span className="text-lg font-semibold text-slate-900 dark:text-white">Drop an image or click to browse</span>
        <span className="mt-1 text-sm text-slate-500">JPG, PNG, TIFF · up to 15 MB. Paste works too.</span>
        <input className="sr-only" type="file" accept=".jpg,.jpeg,.png,.tif,.tiff,image/*" onChange={(event) => take(event.target.files)} />
      </label>
      {samples}
    </div>
  );
}
