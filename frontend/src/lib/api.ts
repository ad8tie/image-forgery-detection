import { API_BASE, USE_MOCKS } from "./config";

export type Health = {
  status: string;
  model_ready: boolean;
  detail: string;
  connected: boolean;
};

export type ElaRegion = {
  x: number;
  y: number;
  w: number;
  h: number;
  severity: "low" | "elevated" | string;
  mean_error: number;
};

export type PredictResult = {
  predicted_class: string;
  model_score: number;
  score: number;
  label: string;
  threshold: number;
  score_label: string;
  positive_class: string;
  explanation: string;
  ela_png_base64: string;
  ela_map_png_base64: string;
  model_ready: boolean;
  ela_quality: number;
  ela_scale: number;
  inference_ms: number;
  image_width: number;
  image_height: number;
  file_size_bytes: number;
  sha256: string;
  ela_stats: {
    mean_error: number;
    max_error: number;
    histogram: number[];
    uniform_area_pct: number;
  };
  regions: ElaRegion[];
  source: "live";
};

export type MetricsPayload = {
  status: string;
  metrics: Record<string, unknown> | null;
  history: { epochs?: Array<Record<string, number>> } | null;
  message: string;
};

async function readError(response: Response) {
  try {
    const body = await response.json();
    if (body && typeof body.detail === "string") return body.detail;
  } catch {
    /* not json */
  }
  return "The server could not complete that request.";
}

export async function getHealth(): Promise<Health> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error(await readError(response));
    const body = await response.json();
    return { ...body, connected: true };
  } catch {
    return {
      status: "offline",
      model_ready: false,
      detail: "Backend is not reachable.",
      connected: false,
    };
  }
}

export async function getMetrics(): Promise<MetricsPayload> {
  if (USE_MOCKS) {
    try {
      const response = await fetch(`${API_BASE}/api/metrics`);
      if (!response.ok) throw new Error(await readError(response));
      const body = (await response.json()) as MetricsPayload;
      if (body.status !== "complete" || !body.metrics) {
        return {
          status: "pending",
          metrics: null,
          history: null,
          message: "Train the model to see results.",
        };
      }
      return body;
    } catch {
      return {
        status: "pending",
        metrics: null,
        history: null,
        message: "Train the model to see results.",
      };
    }
  }
  const response = await fetch(`${API_BASE}/api/metrics`);
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getDatasetStatus(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/api/dataset/status`);
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function predictImage(file: File, quality: number, scale: number): Promise<PredictResult> {
  const body = new FormData();
  body.append("file", file);
  body.append("quality", String(quality));
  body.append("scale", String(scale));
  const response = await fetch(`${API_BASE}/predict`, { method: "POST", body });
  if (!response.ok) throw new Error(await readError(response));
  const payload = await response.json();
  return { ...payload, source: "live" };
}
