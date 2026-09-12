"use client";

import React, { useState } from "react";
import {
  LunarCourtVerdict,
  LunarDNA,
  BlindAudit,
  GraphTopology
} from "../../types";
import { Scale, Dna, EyeOff, Network, Download, CheckCircle, AlertCircle, XCircle, ExternalLink } from "lucide-react";
import { revealBlindAudit } from "../../lib/api";

interface ZeroDayPanelProps {
  courtVerdicts: LunarCourtVerdict[];
  courtSummary: {
    ACCEPT: number;
    UNCERTAIN: number;
    REJECT: number;
  };
  dna: LunarDNA;
  blindAudit?: BlindAudit;
  graphTopology: GraphTopology;
  sessionId: string;
  selectedMatchId?: number;
  onSelectMatch: (matchId: number) => void;
}

export const ZeroDayPanel: React.FC<ZeroDayPanelProps> = ({
  courtVerdicts,
  courtSummary,
  dna,
  blindAudit,
  graphTopology,
  sessionId,
  selectedMatchId,
  onSelectMatch,
}) => {
  const [activeTab, setActiveTab] = useState<"court" | "dna" | "blind" | "graph">("court");
  const [revealedAudit, setRevealedAudit] = useState<BlindAudit | undefined>(undefined);
  const [revealError, setRevealError] = useState<string | null>(null);
  const selectedVerdict = courtVerdicts.find((verdict) => verdict.match_id === selectedMatchId) ?? courtVerdicts[0];
  const displayedBlindAudit = revealedAudit ?? blindAudit;

  const handleReveal = async () => {
    try {
      setRevealError(null);
      setRevealedAudit(await revealBlindAudit(sessionId));
    } catch (error) {
      setRevealError(error instanceof Error ? error.message : "Blind reveal unavailable");
    }
  };

  const downloadCertificate = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(
        JSON.stringify(
          {
            mission: "ISRO Chandrayaan-2 Optical Correspondence",
            problem_statement: "SIH26166",
            team: "TEAM ZERODAY",
            certificate_id: dna.certificate_id,
            canonical_hash: dna.canonical_hash,
            dna_vector: dna.dna_vector,
            physical_parameters: {
              scale_factor: dna.scale_factor,
              rotation_deg: dna.rotation_deg,
              condition_number_log10: dna.matrix_condition_log10,
              spatial_entropy: dna.spatial_entropy,
              mean_residual_px: dna.mean_residual_px,
              residual_variance: dna.residual_variance,
              residual_skewness: dna.residual_skewness,
              mutual_information: dna.mutual_information,
            },
            timestamp: new Date().toISOString(),
          },
          null,
          2
        )
      );
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `${dna.certificate_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const dnaFeatures = [
    { label: "Isotropic Scale Factor", value: dna.scale_factor.toFixed(3), norm: dna.dna_vector[0] },
    { label: "Principal Rotation Angle", value: `${dna.rotation_deg.toFixed(1)}°`, norm: dna.dna_vector[1] },
    { label: "Matrix Conditioning (log10)", value: dna.matrix_condition_log10.toFixed(2), norm: dna.dna_vector[2] },
    { label: "Grid Distribution Entropy", value: (dna.spatial_entropy * 100).toFixed(1) + "%", norm: dna.dna_vector[3] },
    { label: "Mean Residual Error", value: `${dna.mean_residual_px.toFixed(2)} px`, norm: dna.dna_vector[4] },
    { label: "Error Variance Moment", value: dna.residual_variance.toFixed(2), norm: dna.dna_vector[5] },
    { label: "Error Skewness Moment", value: dna.residual_skewness.toFixed(2), norm: dna.dna_vector[6] },
    { label: "Normalized Mutual Info", value: dna.mutual_information.toFixed(3), norm: dna.dna_vector[7] },
  ];

  return (
    <div className="panel p-5 space-y-4">
      {/* Tab Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-2.5">
        <div className="seg">
          <button
            onClick={() => setActiveTab("court")}
            className={`transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === "court"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Scale className="h-3.5 w-3.5" />
            <span>Lunar Court ({courtVerdicts.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("dna")}
            className={`transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === "dna"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Dna className="h-3.5 w-3.5" />
            <span>Lunar DNA</span>
          </button>
          <button
            onClick={() => setActiveTab("blind")}
            className={`transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === "blind"
                ? "seg-active text-warn"
                : "seg-idle"
            }`}
          >
            <EyeOff className="h-3.5 w-3.5" />
            <span>Blind Audit</span>
          </button>
          <button
            onClick={() => setActiveTab("graph")}
            className={`transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === "graph"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Network className="h-3.5 w-3.5" />
            <span>Topology Graph</span>
          </button>
        </div>

        <span className="text-[10px] font-mono text-muted">TEAM ZERODAY INNOVATION SUITE</span>
      </div>

      {/* Tab 1: Lunar Correspondence Court */}
      {activeTab === "court" && (
        <div className="space-y-3">
          {/* Summary Badges */}
          <div className="grid grid-cols-3 gap-2">
            <div className="panel-inset border-ok/30 p-2.5 flex items-center justify-between font-mono">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-ok" />
                <span className="text-xs text-fg-soft">ACCEPTED</span>
              </div>
              <span className="text-base font-bold text-ok">{courtSummary.ACCEPT}</span>
            </div>
            <div className="panel-inset border-warn/30 p-2.5 flex items-center justify-between font-mono">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-warn" />
                <span className="text-xs text-fg-soft">UNCERTAIN</span>
              </div>
              <span className="text-base font-bold text-warn">{courtSummary.UNCERTAIN}</span>
            </div>
            <div className="panel-inset border-danger/30 p-2.5 flex items-center justify-between font-mono">
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-danger" />
                <span className="text-xs text-fg-soft">REJECTED</span>
              </div>
              <span className="text-base font-bold text-danger">{courtSummary.REJECT}</span>
            </div>
          </div>

          {/* Court Verdicts Table */}
          {selectedVerdict && (
            <div className="panel-inset border-accent-line p-3.5 space-y-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="eyebrow text-accent">Selected correspondence · match #{selectedVerdict.match_id}</div>
                  <div className="mt-1 text-sm font-semibold text-fg">Why this point was {selectedVerdict.verdict.toLowerCase()}</div>
                </div>
                <span className={`chip ${selectedVerdict.verdict === "ACCEPT" ? "text-ok" : selectedVerdict.verdict === "UNCERTAIN" ? "text-warn" : "text-danger"}`}>
                  {selectedVerdict.verdict}
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
                <div><span className="text-dim block">SOURCE</span><span className="text-fg-soft">({selectedVerdict.src_pt[0].toFixed(2)}, {selectedVerdict.src_pt[1].toFixed(2)})</span></div>
                <div><span className="text-dim block">REFERENCE</span><span className="text-fg-soft">({selectedVerdict.ref_pt[0].toFixed(2)}, {selectedVerdict.ref_pt[1].toFixed(2)})</span></div>
                <div><span className="text-dim block">RESIDUAL</span><span className="text-fg-soft">{selectedVerdict.transfer_residual_px.toFixed(3)} px</span></div>
                <div><span className="text-dim block">CONFIDENCE</span><span className="text-fg-soft">{(selectedVerdict.confidence_score * 100).toFixed(1)}%</span></div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
                <div><span className="text-dim block">APPEARANCE</span><span className="text-fg-soft">{selectedVerdict.evidence_photometric.toFixed(3)}</span></div>
                <div><span className="text-dim block">GEOMETRY</span><span className="text-fg-soft">{selectedVerdict.evidence_local_geometry.toFixed(3)}</span></div>
                <div><span className="text-dim block">CONTEXT</span><span className="text-fg-soft">{selectedVerdict.evidence_context_ratio.toFixed(3)}</span></div>
                <div><span className="text-dim block">RESIDUAL EVIDENCE</span><span className="text-fg-soft">{selectedVerdict.evidence_global_residual.toFixed(3)}</span></div>
              </div>
              <p className="text-[11px] text-muted">{selectedVerdict.decision_rationale}</p>
            </div>
          )}
          <div className="max-h-60 overflow-y-auto rounded-lg border border-line font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead className="bg-base-deep/90 sticky top-0 border-b border-line text-[10px] text-muted uppercase">
                <tr>
                  <th className="p-2">ID</th>
                  <th className="p-2">Verdict</th>
                  <th className="p-2">Score</th>
                  <th className="p-2">Photometric</th>
                  <th className="p-2">Local Affine</th>
                  <th className="p-2">Context Ratio</th>
                  <th className="p-2">Residual</th>
                  <th className="p-2">Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line bg-base-deep/50">
                {courtVerdicts.slice(0, 30).map((v) => (
                  <tr key={v.match_id} onClick={() => onSelectMatch(v.match_id)} className={`hover:bg-surface cursor-pointer ${selectedVerdict?.match_id === v.match_id ? "bg-accent-soft/40" : ""}`}>
                    <td className="p-2 text-muted">#{v.match_id}</td>
                    <td className="p-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          v.verdict === "ACCEPT"
                            ? "bg-ok/15 text-ok"
                            : v.verdict === "UNCERTAIN"
                            ? "bg-warn/15 text-warn"
                            : "bg-danger/15 text-danger"
                        }`}
                      >
                        {v.verdict}
                      </span>
                    </td>
                    <td className="p-2 text-fg">{(v.confidence_score * 100).toFixed(0)}%</td>
                    <td className="p-2 text-fg-soft">{v.evidence_photometric.toFixed(2)}</td>
                    <td className="p-2 text-fg-soft">{v.evidence_local_geometry.toFixed(2)}</td>
                    <td className="p-2 text-fg-soft">{v.evidence_context_ratio.toFixed(2)}</td>
                    <td className="p-2 text-fg-soft">{v.transfer_residual_px.toFixed(2)} px</td>
                    <td className="p-2 text-muted text-[11px] max-w-xs truncate" title={v.decision_rationale}>
                      {v.decision_rationale}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Lunar Correspondence DNA */}
      {activeTab === "dna" && (
        <div className="space-y-3">
          <div className="panel-inset border-accent-line p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 font-mono">
            <div>
              <div className="text-[10px] text-muted uppercase">CANONICAL REGISTRATION SIGNATURE</div>
              <div className="text-base font-bold text-accent tracking-wider">
                {dna.canonical_hash}
              </div>
              <div className="text-[10px] text-dim mt-0.5">CERTIFICATE ID: {dna.certificate_id}</div>
              <div className="text-[10px] text-muted mt-2">Deterministic signature generated from this registration&apos;s computed correspondence and geometric properties.</div>
            </div>
            <button
              onClick={downloadCertificate}
              className="px-3.5 py-1.5 rounded-lg btn-ghost !py-2 !px-3.5 text-accent-strong text-xs font-semibold flex items-center space-x-1.5 transition cursor-pointer"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Certificate</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 font-mono text-xs">
            {dnaFeatures.map((f, idx) => (
              <div key={idx} className="panel-inset p-2.5">
                <div className="flex justify-between text-muted mb-1">
                  <span>{f.label}</span>
                  <span className="text-accent-strong font-bold">{f.value}</span>
                </div>
                <div className="w-full bg-line-strong rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-accent h-full rounded-full"
                    style={{ width: `${Math.min(100, Math.max(5, (f.norm || 0) * 100))}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Blind Lunar Test Audit */}
      {activeTab === "blind" && (
        <div className="space-y-3 font-mono text-xs">
          {displayedBlindAudit ? (
            <>
              <div className="panel-inset border-warn/30 p-3.5 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-muted uppercase block">BLIND EVALUATION GRADE</span>
                  <span className="text-sm font-bold text-warn">{displayedBlindAudit.blind_accuracy_grade}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-muted uppercase block">SCALE RATIO ERROR</span>
                  <span className="text-sm font-bold text-ok">
                    {displayedBlindAudit.scale_error_percentage === undefined ? "N/A" : `${displayedBlindAudit.scale_error_percentage.toFixed(2)}%`}
                  </span>
                </div>
              </div>

              <div className="panel-inset p-3 space-y-2">
                <div className="text-[11px] text-fg-soft font-semibold uppercase border-b border-line pb-1">
                  BLIND ESTIMATION &amp; REVEAL
                </div>
                <div className="grid grid-cols-2 gap-3 text-muted">
                  <div>
                    <span className="text-dim block">ESTIMATED SCALE (BLIND):</span>
                    <span className="text-fg font-bold">{displayedBlindAudit.blind_estimated_scale}x</span>
                  </div>
                  <div>
                    <span className="text-dim block">TRUE SENSOR RATIO:</span>
                    <span className="text-fg font-bold">{displayedBlindAudit.true_scale_ratio === undefined ? "N/A" : `${displayedBlindAudit.true_scale_ratio}x`}</span>
                  </div>
                  <div>
                    <span className="text-dim block">ESTIMATED ROTATION:</span>
                    <span className="text-fg font-bold">{displayedBlindAudit.blind_estimated_rotation_deg}°</span>
                  </div>
                  <div>
                    <span className="text-dim block">GROUND TRUTH SENSORS:</span>
                    <span className="text-fg font-bold">
                      {displayedBlindAudit.true_sensor_source && displayedBlindAudit.true_sensor_reference ? `${displayedBlindAudit.true_sensor_source} → ${displayedBlindAudit.true_sensor_reference}` : "Metadata hidden"}
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-[11px] text-muted border-t border-line pt-1.5">
                  {displayedBlindAudit.audit_notes}
                </div>
                {!revealedAudit && <button onClick={handleReveal} className="btn-ghost !py-2 text-xs"><ExternalLink className="h-3.5 w-3.5" /> Reveal stored metadata</button>}
                {revealError && <p className="text-danger">{revealError}</p>}
              </div>
            </>
          ) : (
            <div className="p-6 text-center text-dim panel-inset">
              Blind mode was not active during this run. Enable &quot;Blind Lunar Evaluation Mode&quot; in the controls panel to evaluate autonomous scale estimation without sensor metadata.
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Lunar Correspondence Graph Summary */}
      {activeTab === "graph" && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-3 gap-2.5">
            <div className="panel-inset p-3">
              <span className="text-[10px] text-muted block uppercase">DELAUNAY NODES</span>
              <span className="text-lg font-bold text-accent-strong">{graphTopology.nodes.length}</span>
            </div>
            <div className="panel-inset p-3">
              <span className="text-[10px] text-muted block uppercase">TOPOLOGICAL EDGES</span>
              <span className="text-lg font-bold text-accent-strong">{graphTopology.edges.length}</span>
            </div>
            <div className="panel-inset p-3">
              <span className="text-[10px] text-muted block uppercase">STRUCTURAL INTEGRITY</span>
              <span className="text-lg font-bold text-ok">
                {(graphTopology.structural_integrity_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="panel-inset p-3 text-[11px] text-muted">
            Graph topology represents multi-point relative geometry across lunar craters. The Delaunay mesh preserves triangular neighborhood angles and length ratios, identifying out-of-plane relief deformation caused by high crater rim slopes.
          </div>
        </div>
      )}
    </div>
  );
};
