import {
  IngestionUploadResponse,
  SamplePairInfo,
  PipelineResponse
} from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function checkHealth(): Promise<{ status: string; team: string }> {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error("Health check failed");
    return await res.json();
  } catch (err) {
    return { status: "offline", team: "TEAM ZERODAY" };
  }
}

export async function getSamplePairs(): Promise<SamplePairInfo[]> {
  const res = await fetch(`${API_BASE}/api/ingest/samples`);
  if (!res.ok) throw new Error("Failed to fetch sample pairs");
  return await res.json();
}

export async function loadSamplePair(sampleId: string): Promise<{
  session_id: string;
  source_preview: string;
  reference_preview: string;
  source_info: { width: number; height: number; sensor: string };
  reference_info: { width: number; height: number; sensor: string };
}> {
  const formData = new FormData();
  formData.append("sample_id", sampleId);

  const res = await fetch(`${API_BASE}/api/ingest/load-sample`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to load sample" }));
    throw new Error(err.detail || "Failed to load sample");
  }

  return await res.json();
}

export async function uploadImage(
  file: File,
  role: "source" | "reference",
  sensor: string,
  sessionId?: string
): Promise<IngestionUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("role", role);
  formData.append("sensor", sensor);
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const res = await fetch(`${API_BASE}/api/ingest/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }

  return await res.json();
}

export interface RunPipelineOptions {
  sessionId: string;
  preprocessingMode: string;
  detectorType: string;
  descriptorType: string;
  maxFeatures: number;
  ratioThreshold: number;
  ransacThresholdPx: number;
  preferredModel: string;
  blindMode: boolean;
  sourceSensor: string;
  referenceSensor: string;
  sourceGsd: number;
  referenceGsd: number;
}

export async function runPipeline(opts: RunPipelineOptions): Promise<PipelineResponse> {
  const res = await fetch(`${API_BASE}/api/pipeline/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: opts.sessionId,
      preprocessing_mode: opts.preprocessingMode,
      detector_type: opts.detectorType,
      descriptor_type: opts.descriptorType,
      max_features: opts.maxFeatures,
      ratio_threshold: opts.ratioThreshold,
      ransac_threshold_px: opts.ransacThresholdPx,
      preferred_model: opts.preferredModel,
      blind_mode: opts.blindMode,
      source_sensor: opts.sourceSensor,
      reference_sensor: opts.referenceSensor,
      source_gsd: opts.sourceGsd,
      reference_gsd: opts.referenceGsd,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Correspondence execution failed" }));
    throw new Error(err.detail || "Correspondence execution failed");
  }

  return await res.json();
}

export async function revealBlindAudit(sessionId: string): Promise<NonNullable<PipelineResponse["blind_audit"]>> {
  const res = await fetch(`${API_BASE}/api/pipeline/reveal-blind`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Blind reveal unavailable" }));
    throw new Error(err.detail || "Blind reveal unavailable");
  }
  return await res.json();
}
