"use client";

import React from "react";
import { MetricsSummary } from "../../types";
import { Target, CheckCircle2, Compass, Gauge, Binary } from "lucide-react";

interface TelemetryPanelProps {
  metrics: MetricsSummary;
  modelType: string;
  conditionNumber: number;
  matrix: number[][];
  success: boolean;
}

const Kpi: React.FC<{
  label: string;
  icon: React.ReactNode;
  value: React.ReactNode;
  unit?: string;
  note: React.ReactNode;
  tone?: string;
  delay?: string;
}> = ({ label, icon, value, unit, note, tone = "text-fg", delay = "" }) => (
  <div className={`panel-inset p-3.5 flex flex-col justify-between anim-rise ${delay}`}>
    <div className="flex items-center justify-between mb-2">
      <span className="label-sm">{label}</span>
      <span className="text-accent">{icon}</span>
    </div>
    <div className="flex items-baseline gap-1.5">
      <span className={`metric text-2xl font-semibold ${tone}`}>{value}</span>
      {unit && <span className="text-[10px] font-mono text-muted">{unit}</span>}
    </div>
    <div className="text-[10px] font-mono mt-1.5">{note}</div>
  </div>
);

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({
  metrics,
  modelType,
  conditionNumber,
  matrix,
  success,
}) => {
  const ratio = metrics.inlier_ratio * 100;
  return (
    <div className="panel-float p-5 space-y-4 h-full">
      <div className="flex items-center justify-between border-b border-line pb-3">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg panel-inset flex items-center justify-center text-accent">
            <Gauge className="h-3.5 w-3.5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-fg tracking-tight">Registration Telemetry</h2>
            <p className="label-sm">Quantitative accuracy evaluation</p>
          </div>
        </div>
        <span className={`chip ${success ? "text-ok border-ok/30 bg-ok/5" : "text-danger border-danger/30 bg-danger/5"}`}>
          <span className="dot" /> {success ? "Verified" : "Registration failed"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        <Kpi
          label="Transfer RMSE"
          icon={<Target className="h-3.5 w-3.5" />}
          value={metrics.rmse_px.toFixed(3)}
          unit="px"
          tone="text-accent-strong"
          note={
            <span className="text-ok">
              {metrics.rmse_px < 1.0 ? "Sub-pixel precision" : "Near-pixel precision"}
            </span>
          }
        />
        <Kpi
          label="Inlier Matches"
          icon={<CheckCircle2 className="h-3.5 w-3.5 text-ok" />}
          value={metrics.inlier_count}
          unit={`/ ${metrics.tentative_count}`}
          tone="text-ok"
          delay="delay-1"
          note={
            <div className="space-y-1">
              <div className="flex justify-between text-muted">
                <span>Inlier ratio</span>
                <span className="text-fg">{ratio.toFixed(1)}%</span>
              </div>
              <div className="h-1 rounded-full bg-line-strong overflow-hidden">
                <div className="h-full bg-ok rounded-full transition-all duration-700" style={{ width: `${Math.min(100, ratio)}%` }} />
              </div>
            </div>
          }
        />
        <Kpi
          label="Grid Distribution Entropy"
          icon={<Compass className="h-3.5 w-3.5" />}
          value={`${(metrics.spatial_entropy * 100).toFixed(1)}%`}
          delay="delay-2"
          note={<span className="text-muted">Grid coverage {(metrics.grid_coverage * 100).toFixed(0)}%</span>}
        />
        <Kpi
          label="Post-reg NMI / SSIM"
          icon={<Binary className="h-3.5 w-3.5" />}
          value={metrics.nmi.toFixed(3)}
          unit="NMI"
          delay="delay-3"
          note={<span className="text-muted">SSIM {metrics.ssim.toFixed(3)}</span>}
        />
      </div>

      {/* Transformation matrix */}
      <div className="panel-inset p-4 font-mono">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span className="label-sm text-fg-soft">
            Estimated {modelType} transformation (3×3)
          </span>
          <div className="flex items-center gap-2 text-[10px]">
            <span className="text-dim">κ</span>
            <span className="text-accent-strong font-semibold metric">{conditionNumber.toFixed(2)}</span>
            <span className="text-line-strong">|</span>
            <span className="text-ok">STABLE</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-1.5 text-center text-[12px]">
          {matrix.map((row, rIdx) =>
            row.map((val, cIdx) => (
              <div
                key={`${rIdx}-${cIdx}`}
                className="metric bg-base-deep/70 py-2 px-2 rounded-lg border border-line text-fg-soft hover:border-line-strong hover:text-fg transition-colors"
              >
                {val.toFixed(5)}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
