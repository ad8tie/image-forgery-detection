import { motion, useReducedMotion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import { AdvancedDetails } from "../components/AdvancedDetails";
import { CtaBanner } from "../components/CtaBanner";
import { FindingsCard } from "../components/FindingsCard";
import { Hero } from "../components/Hero";
import { Histogram } from "../components/Histogram";
import { ImageInspector } from "../components/ImageInspector";
import { RecentChecks, type RecentItem } from "../components/RecentChecks";
import { ScanOverlay } from "../components/ScanOverlay";
import { StepsTimeline } from "../components/StepsTimeline";
import { UploadDropzone } from "../components/UploadDropzone";
import { VerdictCard } from "../components/VerdictCard";
import { predictImage, type PredictResult } from "../lib/api";
import { sampleMakers } from "../lib/samples";

const STORAGE_KEY = "recent-checks";

function readRecent(): RecentItem[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.slice(0, 5) : [];
  } catch {
    return [];
  }
}

export default function CheckImage() {
  const reduce = useReducedMotion();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResult | null>(null);
  const [quality, setQuality] = useState(90);
  const [scale, setScale] = useState(10);
  const [recent, setRecent] = useState<RecentItem[]>([]);
  const [recalled, setRecalled] = useState<RecentItem | null>(null);

  useEffect(() => setRecent(readRecent()), []);

  const choose = useCallback((next: File) => {
    const ok = /\.(jpe?g|png|tiff?)$/i.test(next.name) || next.type.startsWith("image/");
    if (!ok) {
      setError("Please choose a JPG, PNG, or TIFF image.");
      return;
    }
    if (next.size > 15 * 1024 * 1024) {
      setError("That file is larger than 15 MB.");
      return;
    }
    setFile(next);
    setPreview(URL.createObjectURL(next));
    setResult(null);
    setError("");
    setRecalled(null);
  }, []);

  async function analyze(current = file, q = quality, s = scale) {
    if (!current) return;
    setLoading(true);
    setError("");
    try {
      const payload = await predictImage(current, q, s);
      setResult(payload);
      const thumb = await thumbnail(preview || URL.createObjectURL(current));
      const item: RecentItem = {
        id: `${Date.now()}`,
        name: current.name,
        label: payload.label,
        score: payload.score,
        thumb,
      };
      const next = [item, ...readRecent().filter((row) => row.name !== item.name)].slice(0, 5);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setRecent(next);
      window.setTimeout(() => document.getElementById("result")?.scrollIntoView({ behavior: reduce ? "auto" : "smooth" }), 50);
    } catch (err) {
      setResult(null);
      const message = err instanceof Error ? err.message : "Analysis failed.";
      setError(/fetch|network|failed/i.test(message) ? "Can't reach the server, is the backend running?" : message);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setFile(null);
    setPreview("");
    setResult(null);
    setError("");
    setRecalled(null);
  }

  function download() {
    if (!result || !file) return;
    const blob = new Blob([JSON.stringify({ file: file.name, ...result }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "image-check-report.json";
    link.click();
    URL.revokeObjectURL(url);
  }

  async function copySummary() {
    if (!result) return;
    const text = `${result.label}\nModel score ${result.score.toFixed(3)}\nThreshold ${result.threshold.toFixed(2)}\n${result.explanation}`;
    await navigator.clipboard.writeText(text);
  }

  return (
    <div className="mx-auto max-w-[1100px] px-5 pb-16">
      {!result && (
        <Hero>
          <UploadDropzone
            onFile={choose}
            samples={
              <div className="mt-4 flex justify-center gap-3">
                {sampleMakers.map((sample) => (
                  <button key={sample.label} type="button" className="rounded-2xl border border-[#E2E8F0] bg-white px-4 py-2 text-sm dark:border-slate-700 dark:bg-slate-900" onClick={() => sample.make().then(choose)}>
                    {sample.label}
                  </button>
                ))}
              </div>
            }
          />
        </Hero>
      )}
      {file && result && (
        <div className="pt-6">
          <UploadDropzone compact onFile={choose} />
        </div>
      )}
      {file && !result && !loading && (
        <div className="mt-6 text-center">
          <p className="font-semibold">{file.name}</p>
          <button type="button" className="mt-4 rounded-2xl bg-gradient-to-r from-[#4F46E5] to-sky-500 px-5 py-3 font-semibold text-white" onClick={() => analyze()}>
            Analyze image
          </button>
        </div>
      )}
      {loading && preview && <div className="mt-6"><ScanOverlay preview={preview} /></div>}
      {error && <p className="mt-4 text-center text-rose-600">{error}</p>}
      {result && preview && (
        <motion.div id="result" className="mt-8 scroll-mt-24 space-y-6" initial={reduce ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <div className="grid items-start gap-6 lg:grid-cols-2">
            <ImageInspector name={file?.name || "Image"} preview={preview} result={result} />
            <VerdictCard result={result} onReset={reset} onDownload={download} onCopy={copySummary} />
          </div>
          <FindingsCard result={result} />
          <div className="grid gap-4 lg:grid-cols-3">
            <StepsTimeline quality={result.ela_quality} scale={result.ela_scale} />
            {result.ela_stats?.histogram && <Histogram bins={result.ela_stats.histogram} mean={result.ela_stats.mean_error} />}
            <AdvancedDetails
              quality={quality}
              scale={scale}
              sha={result.sha256}
              threshold={result.threshold}
              onQuality={setQuality}
              onScale={setScale}
              onRerun={() => analyze(file, quality, scale)}
            />
          </div>
        </motion.div>
      )}
      {recalled && !result && (
        <p className="mt-6 rounded-2xl border border-[#E2E8F0] bg-white p-4 text-sm dark:border-slate-700 dark:bg-slate-900">
          Saved check: {recalled.name} · {recalled.label} · model score {recalled.score.toFixed(2)}. The image itself was not kept.
        </p>
      )}
      <RecentChecks items={recent} onOpen={setRecalled} />
      <CtaBanner />
      <p className="mt-6 text-center text-sm text-slate-500">This is an AI estimate, not proof of tampering.</p>
    </div>
  );
}

function thumbnail(src: string) {
  return new Promise<string>((resolve) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 64;
      canvas.height = 48;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(image, 0, 0, 64, 48);
      resolve(canvas.toDataURL("image/jpeg", 0.7));
    };
    image.onerror = () => resolve("");
    image.src = src;
  });
}
