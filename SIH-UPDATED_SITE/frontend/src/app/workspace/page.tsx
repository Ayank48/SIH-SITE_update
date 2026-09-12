"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../../components/Header";
import { IngestionPanel } from "../../components/panels/IngestionPanel";
import { ControlsPanel } from "../../components/panels/ControlsPanel";
import { DualViewport } from "../../components/visualizers/DualViewport";
import { RegistrationCurtain } from "../../components/visualizers/RegistrationCurtain";
import { CorrespondenceGraph } from "../../components/visualizers/CorrespondenceGraph";
import { TelemetryPanel } from "../../components/panels/TelemetryPanel";
import { ZeroDayPanel } from "../../components/panels/ZeroDayPanel";
import { VerificationLab } from "../../components/panels/VerificationLab";

import {
  checkHealth,
  getSamplePairs,
  loadSamplePair,
  uploadImage,
  runPipeline
} from "../../lib/api";
import { SamplePairInfo, PipelineResponse } from "../../types";
import { Layers, SlidersHorizontal, Network, AlertTriangle, ScanLine } from "lucide-react";

export default function MissionControlDashboard() {
  const [systemStatus, setSystemStatus] = useState<"online" | "offline">("online");
  const [sessionId, setSessionId] = useState<string>("");
  const [samplePairs, setSamplePairs] = useState<SamplePairInfo[]>([]);
  const [isLoadingSample, setIsLoadingSample] = useState<boolean>(false);

  // Images state
  const [sourcePreview, setSourcePreview] = useState<string | null>(null);
  const [referencePreview, setReferencePreview] = useState<string | null>(null);
  const [sourceSensor, setSourceSensor] = useState<string>("OHRC");
  const [referenceSensor, setReferenceSensor] = useState<string>("TMC2");
  const [sourceGsd, setSourceGsd] = useState<number>(0.25);
  const [referenceGsd, setReferenceGsd] = useState<number>(5.0);
  const [sourceInfo, setSourceInfo] = useState<{ width: number; height: number; sensor: string } | undefined>();
  const [referenceInfo, setReferenceInfo] = useState<{ width: number; height: number; sensor: string } | undefined>();

  // Pipeline control parameters
  const [preprocessingMode, setPreprocessingMode] = useState<string>("clahe");
  const [detectorType, setDetectorType] = useState<string>("sift");
  const [descriptorType, setDescriptorType] = useState<string>("sift");
  const [maxFeatures, setMaxFeatures] = useState<number>(1500);
  const [ratioThreshold, setRatioThreshold] = useState<number>(0.85);
  const [ransacThresholdPx, setRansacThresholdPx] = useState<number>(5.0);
  const [preferredModel, setPreferredModel] = useState<string>("auto");
  const [blindMode, setBlindMode] = useState<boolean>(false);

  // Pipeline execution results
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [processingDurationMs, setProcessingDurationMs] = useState<number | undefined>();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Active Center View Tab
  const [centerTab, setCenterTab] = useState<"dual" | "curtain" | "graph">("dual");
  const [selectedMatchId, setSelectedMatchId] = useState<number | undefined>();

  useEffect(() => {
    // Check backend health and fetch sample benchmark datasets
    checkHealth().then((h) => setSystemStatus(h.status === "online" ? "online" : "offline"));
    getSamplePairs()
      .then((pairs) => {
        setSamplePairs(pairs);
        // Auto-load benchmark 1 on startup for instant visual verification
        if (pairs.length > 0) {
          handleLoadSample(pairs[0].sample_id);
        }
      })
      .catch(() => {});
  }, []);

  const handleSensorChange = (role: "source" | "reference", sensor: string, gsd: number) => {
    if (role === "source") {
      setSourceSensor(sensor);
      setSourceGsd(gsd);
    } else {
      setReferenceSensor(sensor);
      setReferenceGsd(gsd);
    }
  };

  const handleFileUpload = async (file: File, role: "source" | "reference") => {
    try {
      setErrorMessage(null);
      const res = await uploadImage(
        file,
        role,
        role === "source" ? sourceSensor : referenceSensor,
        sessionId
      );
      setSessionId(res.session_id);
      if (role === "source") {
        setSourcePreview(res.info.preview_base64);
        setSourceInfo({
          width: res.info.width,
          height: res.info.height,
          sensor: res.info.sensor_name,
        });
      } else {
        setReferencePreview(res.info.preview_base64);
        setReferenceInfo({
          width: res.info.width,
          height: res.info.height,
          sensor: res.info.sensor_name,
        });
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to upload image");
    }
  };

  const handleLoadSample = async (sampleId: string) => {
    try {
      setIsLoadingSample(true);
      setErrorMessage(null);
      const res = await loadSamplePair(sampleId);
      setSessionId(res.session_id);
      setSourcePreview(res.source_preview);
      setReferencePreview(res.reference_preview);
      setSourceInfo(res.source_info);
      setReferenceInfo(res.reference_info);
      setResult(null);
      setProcessingDurationMs(undefined);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load sample benchmark pair");
    } finally {
      setIsLoadingSample(false);
    }
  };

  const handleControlChange = (key: string, value: any) => {
    if (key === "preprocessingMode") setPreprocessingMode(value);
    if (key === "detectorType") setDetectorType(value);
    if (key === "descriptorType") setDescriptorType(value);
    if (key === "maxFeatures") setMaxFeatures(value);
    if (key === "ratioThreshold") setRatioThreshold(value);
    if (key === "ransacThresholdPx") setRansacThresholdPx(value);
    if (key === "preferredModel") setPreferredModel(value);
    if (key === "blindMode") setBlindMode(value);
  };

  const handleExecute = async () => {
    if (!sessionId || !sourcePreview || !referencePreview) return;
    try {
      setIsProcessing(true);
      setErrorMessage(null);
      const startedAt = performance.now();
      const res = await runPipeline({
        sessionId,
        preprocessingMode,
        detectorType,
        descriptorType,
        maxFeatures,
        ratioThreshold,
        ransacThresholdPx,
        preferredModel,
        blindMode,
        sourceSensor,
        referenceSensor,
        sourceGsd,
        referenceGsd,
      });

      setResult(res);
      setProcessingDurationMs(performance.now() - startedAt);
      // If registration succeeded, default center view to dual viewport
      setCenterTab("dual");
    } catch (err: any) {
      setErrorMessage(err.message || "Correspondence engine failed to converge");
    } finally {
      setIsProcessing(false);
    }
  };

  const canExecute = Boolean(sourcePreview && referencePreview && sessionId);

  const tabs: { id: "dual" | "curtain" | "graph"; label: string; icon: React.ReactNode }[] = [
    { id: "dual", label: "Correspondence Vectors", icon: <Layers className="h-3.5 w-3.5" /> },
    { id: "curtain", label: "Registered Mosaic & Blend", icon: <SlidersHorizontal className="h-3.5 w-3.5" /> },
    { id: "graph", label: "Delaunay Topology Graph", icon: <Network className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="min-h-screen text-fg flex flex-col">
      <Header
        systemStatus={systemStatus}
        sessionId={sessionId}
        isProcessing={isProcessing}
      />

      <main className="flex-1 p-4 lg:p-7 space-y-6 max-w-[1700px] w-full mx-auto anim-fade">
        {/* Page intro */}
        <div className="panel-float technical-grid px-5 py-5 lg:px-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4 overflow-hidden">
          <div>
            <p className="eyebrow mb-2 text-accent">Mission analysis / active workspace</p>
            <h2 className="text-2xl lg:text-3xl font-semibold tracking-[-0.025em] text-fg">Image Correspondence &amp; Registration</h2>
            <p className="mt-1.5 text-xs text-muted max-w-2xl">Inspect cross-sensor matches, verify geometric consensus, and evaluate the registered lunar frame.</p>
          </div>
          {systemStatus === "offline" && !isProcessing && (
            <span className="chip text-danger border-danger/30 bg-danger/5">
              <span className="dot" /> Engine offline — start the backend on :8000
            </span>
          )}
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="panel border-danger/30 p-4 flex items-start gap-3 anim-rise" role="alert">
            <div className="h-8 w-8 rounded-lg bg-danger/10 border border-danger/30 flex items-center justify-center shrink-0">
              <AlertTriangle className="h-4 w-4 text-danger" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="label-sm text-danger mb-0.5">Scientific engine notice</div>
              <p className="text-xs text-fg-soft font-mono break-words">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Section 1: Ingestion & Controls */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-stretch">
          <div className="xl:col-span-7 anim-rise">
            <IngestionPanel
              sourcePreview={sourcePreview}
              referencePreview={referencePreview}
              sourceSensor={sourceSensor}
              referenceSensor={referenceSensor}
              sourceGsd={sourceGsd}
              referenceGsd={referenceGsd}
              sourceInfo={sourceInfo}
              referenceInfo={referenceInfo}
              onSensorChange={handleSensorChange}
              onFileUpload={handleFileUpload}
              onLoadSample={handleLoadSample}
              samplePairs={samplePairs}
              isLoadingSample={isLoadingSample}
            />
          </div>

          <div className="xl:col-span-5 anim-rise delay-1">
            <ControlsPanel
              preprocessingMode={preprocessingMode}
              detectorType={detectorType}
              descriptorType={descriptorType}
              maxFeatures={maxFeatures}
              ratioThreshold={ratioThreshold}
              ransacThresholdPx={ransacThresholdPx}
              preferredModel={preferredModel}
              blindMode={blindMode}
              isProcessing={isProcessing}
              canExecute={canExecute}
              onChange={handleControlChange}
              onExecute={handleExecute}
            />
          </div>
        </div>

        {/* Processing state */}
        {isProcessing && !result && (
          <div className="panel-float p-10 relative overflow-hidden scan anim-rise">
            <div className="flex flex-col items-center text-center gap-3">
              <div className="h-12 w-12 rounded-2xl panel-inset flex items-center justify-center text-accent">
                <ScanLine className="h-5 w-5 anim-pulse-soft" />
              </div>
              <div className="text-sm font-semibold text-fg">Computing correspondence &amp; registration</div>
              <p className="text-xs text-muted font-mono max-w-md">
                Illumination normalization → feature extraction → descriptor matching → geometric verification → warping → evaluation
              </p>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!isProcessing && !result && (
          <div className="panel-float p-10 border-dashed anim-rise delay-2">
            <div className="flex flex-col items-center text-center gap-2">
              <div className="h-12 w-12 rounded-2xl panel-inset flex items-center justify-center text-dim">
                <Layers className="h-5 w-5" />
              </div>
              <div className="text-sm font-medium text-fg-soft">No registration results yet</div>
              <p className="text-xs text-muted max-w-sm">
                Load a benchmark pair or upload source and reference images, tune the engine parameters, then run the correspondence pipeline.
              </p>
            </div>
          </div>
        )}

        {/* Section 2: Visual Registration Workspace */}
        {result && (
          <div className="space-y-5 anim-rise">
            {/* Viewport Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="seg flex-wrap">
                {tabs.map((t, i) => (
                  <button
                    key={t.id}
                    onClick={() => setCenterTab(t.id)}
                    className={`${centerTab === t.id ? "seg-active" : "seg-idle"} flex items-center gap-2 !px-3.5 !py-2`}
                  >
                    <span className={centerTab === t.id ? "text-accent" : "text-dim"}>{t.icon}</span>
                    <span className="text-dim">{i + 1}.</span>
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>
              <span className="eyebrow hidden md:block">Results · session {sessionId.slice(0, 8)}</span>
            </div>

            {/* Active Visualizer */}
            <div key={centerTab} className="anim-fade">
              {centerTab === "dual" && (
                <DualViewport
                  sourceImage={result.source_preview}
                  referenceImage={result.reference_preview}
                  matches={result.matches}
                  sourceDimensions={sourceInfo ? { width: sourceInfo.width, height: sourceInfo.height } : undefined}
                  referenceDimensions={referenceInfo ? { width: referenceInfo.width, height: referenceInfo.height } : undefined}
                />
              )}

              {centerTab === "curtain" && (
                <RegistrationCurtain
                  referenceImage={result.reference_preview}
                  warpedSourceImage={result.warped_source}
                  diffHeatmap={result.diff_heatmap}
                  checkerboard={result.checkerboard}
                  falseColor={result.false_color}
                />
              )}

              {centerTab === "graph" && (
                <CorrespondenceGraph topology={result.graph_topology} onSelectMatch={setSelectedMatchId} />
              )}
            </div>

            {/* Section 3: Telemetry & ZERO-DAY Suite */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
              <div className="lg:col-span-4">
                <TelemetryPanel
                  metrics={result.metrics}
                  modelType={result.model_type}
                  conditionNumber={result.condition_number}
                  matrix={result.transformation_matrix}
                  success={result.success}
                />
              </div>

              <div className="lg:col-span-4">
                <ZeroDayPanel
                  courtVerdicts={result.court_verdicts}
                  courtSummary={result.court_summary}
                  dna={result.dna}
                  blindAudit={result.blind_audit}
                  graphTopology={result.graph_topology}
                  sessionId={sessionId}
                  selectedMatchId={selectedMatchId}
                  onSelectMatch={setSelectedMatchId}
                />
              </div>

              <div className="lg:col-span-4">
                <VerificationLab
                  result={result}
                  sourceDimensions={sourceInfo ? { width: sourceInfo.width, height: sourceInfo.height } : undefined}
                  referenceDimensions={referenceInfo ? { width: referenceInfo.width, height: referenceInfo.height } : undefined}
                  processingDurationMs={processingDurationMs}
                  selectedMatchId={selectedMatchId}
                  onSelectMatch={setSelectedMatchId}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-line py-4 px-6 text-[10px] font-mono text-dim flex flex-wrap justify-between gap-2">
        <span>Chandrayaan-2 Optical Correspondence &amp; Registration Engine</span>
        <span>ISRO · SIH26166 · Team ZeroDay</span>
      </footer>
    </div>
  );
}
