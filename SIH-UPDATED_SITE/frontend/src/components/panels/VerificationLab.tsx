"use client";

import React from "react";
import { Download, MapPinned, ShieldCheck, Timer, TriangleAlert } from "lucide-react";
import { MatchPoint, PipelineResponse } from "../../types";

interface VerificationLabProps {
  result: PipelineResponse;
  sourceDimensions?: { width: number; height: number };
  referenceDimensions?: { width: number; height: number };
  processingDurationMs?: number;
  selectedMatchId?: number;
  onSelectMatch: (matchId: number) => void;
}

const verdictTone = (match: MatchPoint) => {
  if (match.verdict === "ACCEPT") return "bg-ok";
  if (match.verdict === "UNCERTAIN") return "bg-warn";
  return "bg-danger";
};

export const VerificationLab: React.FC<VerificationLabProps> = ({
  result,
  sourceDimensions,
  referenceDimensions,
  processingDurationMs,
  selectedMatchId,
  onSelectMatch,
}) => {
  const selectedMatch = result.matches.find((match) => match.id === selectedMatchId) ?? result.matches[0];
  const selectedVerdict = result.court_verdicts.find((verdict) => verdict.match_id === selectedMatch?.id);
  const sourceWidth = sourceDimensions?.width ?? 1;
  const sourceHeight = sourceDimensions?.height ?? 1;
  const referenceWidth = referenceDimensions?.width ?? 1;
  const referenceHeight = referenceDimensions?.height ?? 1;

  const downloadReport = () => {
    const report = {
      generated_at: new Date().toISOString(),
      session_id: result.session_id,
      status: result.success ? "success" : "failed",
      status_message: result.status_message,
      model_type: result.model_type,
      condition_number: result.condition_number,
      metrics: result.metrics,
      court_summary: result.court_summary,
      dna: result.dna,
      graph: result.graph_topology,
      blind_audit: result.blind_audit ?? null,
      processing_duration_ms: processingDurationMs ?? null,
      source_dimensions: sourceDimensions ?? null,
      reference_dimensions: referenceDimensions ?? null,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `lunar-registration-${result.session_id.slice(0, 8)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="panel-float p-5 space-y-4 h-full">
      <div className="flex items-center justify-between gap-3 border-b border-line pb-3">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg panel-inset flex items-center justify-center text-accent">
            <ShieldCheck className="h-3.5 w-3.5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-fg tracking-tight">Verification Lab</h2>
            <p className="label-sm">Runtime evidence &amp; provenance</p>
          </div>
        </div>
        <button onClick={downloadReport} className="btn-ghost !px-2.5 !py-2 text-[10px]" title="Download runtime report">
          <Download className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Export run</span>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="panel-inset p-3">
          <div className="label-sm">Tentative matches</div>
          <div className="metric mt-1 text-xl text-fg">{result.metrics.tentative_count}</div>
          <div className="text-[10px] text-muted">runtime descriptor matches</div>
        </div>
        <div className="panel-inset p-3">
          <div className="label-sm">Accepted by Court</div>
          <div className="metric mt-1 text-xl text-ok">{result.court_summary.ACCEPT}</div>
          <div className="text-[10px] text-muted">computed verdicts</div>
        </div>
        <div className="panel-inset p-3">
          <div className="label-sm flex items-center gap-1"><MapPinned className="h-3 w-3" /> Coverage</div>
          <div className="metric mt-1 text-xl text-accent-strong">{(result.metrics.grid_coverage * 100).toFixed(1)}%</div>
          <div className="text-[10px] text-muted">occupied 4x4 grid cells</div>
        </div>
        <div className="panel-inset p-3">
          <div className="label-sm flex items-center gap-1"><Timer className="h-3 w-3" /> Runtime</div>
          <div className="metric mt-1 text-xl text-fg">{processingDurationMs === undefined ? "N/A" : `${(processingDurationMs / 1000).toFixed(2)}s`}</div>
          <div className="text-[10px] text-muted">client-measured request time</div>
        </div>
      </div>

      <div className="panel-inset p-3 space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <div className="eyebrow text-accent">Trust map</div>
            <div className="text-[11px] text-muted">Every point is sourced from the returned correspondence set.</div>
          </div>
          <div className="flex gap-2 text-[9px] font-mono text-dim"><span className="text-ok">ACCEPT</span><span className="text-warn">UNCERTAIN</span><span className="text-danger">REJECT</span></div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {[{ label: "SOURCE", width: sourceWidth, height: sourceHeight, x: "src_x", y: "src_y" }, { label: "REFERENCE", width: referenceWidth, height: referenceHeight, x: "ref_x", y: "ref_y" }].map((panel) => (
            <div key={panel.label} className="relative aspect-square rounded-lg overflow-hidden bg-base-deep border border-line">
              <div className="absolute top-2 left-2 z-10 chip !py-0.5 text-[9px]">{panel.label}</div>
              {result.matches.map((match) => {
                const x = Number(match[panel.x as "src_x" | "ref_x"]);
                const y = Number(match[panel.y as "src_y" | "ref_y"]);
                return <button key={`${panel.label}-${match.id}`} aria-label={`Select match ${match.id}`} onClick={() => onSelectMatch(match.id)} className={`absolute h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full ${verdictTone(match)} ${selectedMatch?.id === match.id ? "ring-2 ring-white scale-150" : "opacity-80"}`} style={{ left: `${(x / panel.width) * 100}%`, top: `${(y / panel.height) * 100}%` }} />;
              })}
            </div>
          ))}
        </div>
      </div>

      {selectedMatch && selectedVerdict ? (
        <div className="panel-inset border-accent-line p-3 space-y-2">
          <div className="flex items-center justify-between"><div className="eyebrow text-accent">Why match #{selectedMatch.id}</div><span className="chip">{selectedMatch.verdict}</span></div>
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <span>Descriptor distance <strong className="text-fg">{selectedMatch.distance.toFixed(2)}</strong></span>
            <span>Lowe ratio <strong className="text-fg">{selectedMatch.ratio.toFixed(3)}</strong></span>
            <span>Residual <strong className="text-fg">{selectedVerdict.transfer_residual_px.toFixed(3)} px</strong></span>
            <span>Confidence <strong className="text-fg">{(selectedMatch.confidence * 100).toFixed(1)}%</strong></span>
          </div>
          <p className="text-[11px] text-muted">{selectedVerdict.decision_rationale}</p>
        </div>
      ) : (
        <div className="panel-inset p-3 flex items-center gap-2 text-xs text-muted"><TriangleAlert className="h-4 w-4 text-warn" /> Insufficient evidence for selected-match explanation.</div>
      )}

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-muted">
        <div className="panel-inset p-2.5"><span className="text-dim block">INPUT PROVENANCE</span>{sourceDimensions ? `${sourceWidth}x${sourceHeight}` : "N/A"} → {referenceDimensions ? `${referenceWidth}x${referenceHeight}` : "N/A"}</div>
        <div className="panel-inset p-2.5"><span className="text-dim block">DNA SIGNATURE</span><span className="text-accent-strong break-all">{result.dna.canonical_hash}</span></div>
      </div>
      <div className="text-[10px] text-dim border-t border-line pt-3">Comparative robustness across multiple configurations: Not available in this run. No additional measurements are shown.</div>
    </section>
  );
};