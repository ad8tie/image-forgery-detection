import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Accordion } from "../components/Accordion";
import { EmptyState } from "../components/EmptyState";
import { Skeleton } from "../components/Skeleton";
import { StatCard } from "../components/StatCard";
import { getDatasetStatus, getMetrics, type MetricsPayload } from "../lib/api";

function percent(value: unknown) {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "—";
}

export default function Results() {
  const [data, setData] = useState<MetricsPayload | null>(null);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getMetrics()
      .then(setData)
      .catch(() => setError("Can't reach the server, is the backend running?"));
    getDatasetStatus()
      .then((body) => {
        const value = body.image_count;
        setCount(typeof value === "number" && value > 0 ? value : null);
      })
      .catch(() => setCount(null));
  }, []);

  if (error) {
    return (
      <div className="mx-auto max-w-[1100px] px-5 py-12">
        <EmptyState title="Can't reach the server" body="Can't reach the server, is the backend running?" />
      </div>
    );
  }
  if (!data) {
    return (
      <div className="mx-auto grid max-w-[1100px] gap-4 px-5 py-12 sm:grid-cols-2">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>
    );
  }

  const metrics = data.metrics as {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1?: number;
    loss?: number;
    test_samples?: number;
    confusion_matrix?: number[][];
    class_wise?: Record<string, { precision: number; recall: number; f1: number; support: number }>;
  } | null;
  const ready = data.status === "complete" && metrics;
  const matrix = metrics?.confusion_matrix;
  const history = (data.history?.epochs ?? []).map((row) => ({
    epoch: row.epoch,
    train: row.train_accuracy,
    validation: row.val_accuracy,
    trainLoss: row.train_loss,
    valLoss: row.val_loss,
  }));

  return (
    <div className="mx-auto max-w-[1100px] px-5 py-12">
      <h1 className="text-4xl font-semibold tracking-tight">Model results</h1>
      <p className="mt-3 text-[#64748B]">Numbers appear only after a saved evaluation.</p>
      {!ready && (
        <div className="mt-8">
          <EmptyState title="Train the model to see results" body="From the backend folder, run python -m src.train and then python -m src.evaluate." />
        </div>
      )}
      {ready && metrics && (
        <div className="rise mt-8 space-y-6">
          {count !== null && <p className="text-[#64748B]">Trained on CASIA v2.0 · {count} images</p>}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Accuracy" value={percent(metrics.accuracy)} hint="Share of test images labeled correctly." />
            <StatCard label="Precision" value={percent(metrics.precision)} hint="Of the images called edited, how many were edited." />
            <StatCard label="Recall" value={percent(metrics.recall)} hint="Of the edited images, how many were found." />
            <StatCard label="F1" value={percent(metrics.f1)} hint="A balance of precision and recall." />
          </div>
          {matrix && (
            <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-[0_4px_24px_rgba(15,23,42,0.06)]">
              <h2 className="text-xl font-semibold">Confusion matrix</h2>
              <div className="mt-4 grid max-w-md grid-cols-2 gap-3 text-center">
                {[
                  ["Authentic, called authentic", matrix[0]?.[0]],
                  ["Authentic, called edited", matrix[0]?.[1]],
                  ["Edited, called authentic", matrix[1]?.[0]],
                  ["Edited, called edited", matrix[1]?.[1]],
                ].map(([label, value]) => (
                  <div key={String(label)} className="rounded-2xl bg-slate-50 p-4">
                    <p className="text-sm text-[#64748B]">{label}</p>
                    <p className="mt-1 text-2xl font-semibold">{value ?? "—"}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-[0_4px_24px_rgba(15,23,42,0.06)]">
            <h2 className="text-xl font-semibold">Accuracy over epochs</h2>
            <p className="text-sm text-[#64748B]">Train and validation.</p>
            {history.length > 0 ? (
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history}>
                    <CartesianGrid stroke="#E2E8F0" />
                    <XAxis dataKey="epoch" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Line dataKey="train" name="Train" stroke="#4F46E5" dot={false} />
                    <Line dataKey="validation" name="Validation" stroke="#10B981" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="mt-4 text-[#64748B]">No training history was saved with this evaluation.</p>
            )}
          </div>
          <Accordion title="More metrics">
            <p className="text-sm">Test loss: {typeof metrics.loss === "number" ? metrics.loss.toFixed(4) : "Not saved"}</p>
            <p className="mt-2 text-sm">Test images: {metrics.test_samples ?? "Not saved"}</p>
            {history.length > 0 && (
              <div className="mt-4 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history}>
                    <CartesianGrid stroke="#E2E8F0" />
                    <XAxis dataKey="epoch" />
                    <YAxis />
                    <Tooltip />
                    <Line dataKey="trainLoss" name="Train loss" stroke="#EF4444" dot={false} />
                    <Line dataKey="valLoss" name="Validation loss" stroke="#F59E0B" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
            {metrics.class_wise && (
              <ul className="mt-4 space-y-2 text-sm">
                {Object.entries(metrics.class_wise).map(([name, row]) => (
                  <li key={name}>
                    {name}: precision {row.precision.toFixed(3)}, recall {row.recall.toFixed(3)}, F1 {row.f1.toFixed(3)}, support {row.support}
                  </li>
                ))}
              </ul>
            )}
            <p className="mt-3 text-sm text-[#64748B]">A ROC curve is not saved by the current evaluator, so it is not shown.</p>
          </Accordion>
        </div>
      )}
    </div>
  );
}
