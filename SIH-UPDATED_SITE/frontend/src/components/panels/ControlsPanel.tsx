"use client";

import React from "react";
import { Sliders, EyeOff, Play } from "lucide-react";

interface ControlsPanelProps {
  preprocessingMode: string;
  detectorType: string;
  descriptorType: string;
  maxFeatures: number;
  ratioThreshold: number;
  ransacThresholdPx: number;
  preferredModel: string;
  blindMode: boolean;
  isProcessing: boolean;
  canExecute: boolean;
  onChange: (key: string, value: any) => void;
  onExecute: () => void;
}

const pct = (v: number, min: number, max: number) => `${((v - min) / (max - min)) * 100}%`;

export const ControlsPanel: React.FC<ControlsPanelProps> = ({
  preprocessingMode,
  detectorType,
  descriptorType,
  maxFeatures,
  ratioThreshold,
  ransacThresholdPx,
  preferredModel,
  blindMode,
  isProcessing,
  canExecute,
  onChange,
  onExecute,
}) => {
  return (
    <div className="panel-float p-5 space-y-5 h-full flex flex-col">
      <div className="flex items-center justify-between border-b border-line pb-3">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg panel-inset flex items-center justify-center text-accent">
            <Sliders className="h-3.5 w-3.5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-fg tracking-tight">Correspondence Engine Controls</h2>
            <p className="label-sm">Pipeline parameters</p>
          </div>
        </div>
        <span className="eyebrow hidden sm:block">SIH26166 Tuning</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        <div>
          <label className="label-sm block mb-1.5">Illumination Normalization</label>
          <select
            value={preprocessingMode}
            onChange={(e) => onChange("preprocessingMode", e.target.value)}
            className="field"
          >
            <option value="clahe">CLAHE (Adaptive Contrast)</option>
            <option value="phase_congruency">Phase Congruency (Local Energy)</option>
            <option value="retinex">Multi-Scale Retinex (Homomorphic)</option>
          </select>
        </div>

        <div>
          <label className="label-sm block mb-1.5">Feature Detector &amp; ANMS</label>
          <select
            value={detectorType}
            onChange={(e) => onChange("detectorType", e.target.value)}
            className="field"
          >
            <option value="sift">SIFT Scale-Space + ANMS</option>
            <option value="orb">ORB Multi-Scale + ANMS</option>
            <option value="akaze">AKAZE Nonlinear Diffusion</option>
          </select>
        </div>

        <div>
          <label className="label-sm block mb-1.5">Descriptor Architecture</label>
          <select
            value={descriptorType}
            onChange={(e) => onChange("descriptorType", e.target.value)}
            className="field"
          >
            <option value="sift">SIFT 128-D Descriptors</option>
            <option value="orb">ORB Binary Descriptors</option>
            <option value="akaze">AKAZE Descriptors</option>
            <option value="cfog">CFOG (Orientations mod pi)</option>
          </select>
        </div>

        <div>
          <label className="label-sm block mb-1.5">Transformation Model</label>
          <select
            value={preferredModel}
            onChange={(e) => onChange("preferredModel", e.target.value)}
            className="field"
          >
            <option value="auto">Auto (Condition-guided Selection)</option>
            <option value="homography">Homography (Projective 3x3)</option>
            <option value="affine">Affine (6-DOF 2x3)</option>
          </select>
        </div>
      </div>

      {/* Sliders */}
      <div className="panel-inset p-4 space-y-4">
        <div>
          <div className="flex justify-between items-baseline mb-2">
            <span className="label-sm">Max keypoints (ANMS)</span>
            <span className="metric text-sm text-accent-strong font-semibold">{maxFeatures}</span>
          </div>
          <input
            type="range"
            min={400}
            max={2500}
            step={100}
            value={maxFeatures}
            onChange={(e) => onChange("maxFeatures", parseInt(e.target.value))}
            className="range"
            style={{ ["--pct" as any]: pct(maxFeatures, 400, 2500) }}
          />
        </div>

        <div>
          <div className="flex justify-between items-baseline mb-2">
            <span className="label-sm">Lowe ratio threshold</span>
            <span className="metric text-sm text-accent-strong font-semibold">{ratioThreshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0.65}
            max={0.92}
            step={0.01}
            value={ratioThreshold}
            onChange={(e) => onChange("ratioThreshold", parseFloat(e.target.value))}
            className="range"
            style={{ ["--pct" as any]: pct(ratioThreshold, 0.65, 0.92) }}
          />
        </div>

        <div>
          <div className="flex justify-between items-baseline mb-2">
            <span className="label-sm">RANSAC reprojection tolerance</span>
            <span className="metric text-sm text-accent-strong font-semibold">
              {ransacThresholdPx.toFixed(1)} <span className="text-muted text-[10px]">px</span>
            </span>
          </div>
          <input
            type="range"
            min={1.5}
            max={8.0}
            step={0.5}
            value={ransacThresholdPx}
            onChange={(e) => onChange("ransacThresholdPx", parseFloat(e.target.value))}
            className="range"
            style={{ ["--pct" as any]: pct(ransacThresholdPx, 1.5, 8.0) }}
          />
        </div>
      </div>

      {/* Blind mode + Execute */}
      <div className="mt-auto flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-4 border-t border-line">
        <label
          className={`flex items-center gap-3 cursor-pointer select-none rounded-xl px-3 py-2.5 border transition-all ${
            blindMode
              ? "border-warn/40 bg-warn/5"
              : "border-transparent hover:bg-surface"
          }`}
        >
          <input
            type="checkbox"
            checked={blindMode}
            onChange={(e) => onChange("blindMode", e.target.checked)}
            className="w-4 h-4 rounded accent-[#e0b45c] cursor-pointer"
          />
          <EyeOff className={`h-4 w-4 ${blindMode ? "text-warn" : "text-dim"}`} />
          <div className="leading-tight">
            <div className={`text-xs font-medium ${blindMode ? "text-warn" : "text-fg-soft"}`}>
              Blind Lunar Evaluation Mode
            </div>
            <div className="text-[10px] text-dim">Strips sensor metadata before matching</div>
          </div>
        </label>

        <button
          onClick={onExecute}
          disabled={!canExecute || isProcessing}
          className="btn-primary w-full sm:w-auto sm:min-w-[240px]"
        >
          {isProcessing ? (
            <>
              <span className="h-4 w-4 border-2 border-black/15 border-t-black/70 rounded-full animate-spin" />
              <span>Computing registration…</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Run Correspondence Pipeline</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
