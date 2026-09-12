"use client";

import React, { useState, useRef } from "react";
import { SlidersHorizontal, Flame, Grid, Eye, Sparkles } from "lucide-react";

interface RegistrationCurtainProps {
  referenceImage: string;
  warpedSourceImage: string;
  diffHeatmap: string;
  checkerboard: string;
  falseColor: string;
}

export const RegistrationCurtain: React.FC<RegistrationCurtainProps> = ({
  referenceImage,
  warpedSourceImage,
  diffHeatmap,
  checkerboard,
  falseColor,
}) => {
  const [mode, setMode] = useState<"curtain" | "diff" | "checker" | "false_color">("curtain");
  const [sliderPos, setSliderPos] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (mode !== "curtain" || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    setSliderPos((x / rect.width) * 100);
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (mode !== "curtain" || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.touches[0].clientX - rect.left, rect.width));
    setSliderPos((x / rect.width) * 100);
  };

  return (
    <div className="panel-float p-4 space-y-3">
      {/* Header & Blend Mode Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono font-bold text-fg uppercase">
            REGISTERED LUNAR MOSAIC & PRODUCT BLEND
          </span>
        </div>

        <div className="seg">
          <button
            onClick={() => setMode("curtain")}
            className={`transition flex items-center space-x-1 cursor-pointer ${
              mode === "curtain"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <SlidersHorizontal className="h-3 w-3" />
            <span>Split Slider</span>
          </button>
          <button
            onClick={() => setMode("diff")}
            className={`transition flex items-center space-x-1 cursor-pointer ${
              mode === "diff"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Flame className="h-3 w-3" />
            <span>Diff Heatmap</span>
          </button>
          <button
            onClick={() => setMode("checker")}
            className={`transition flex items-center space-x-1 cursor-pointer ${
              mode === "checker"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Grid className="h-3 w-3" />
            <span>Checkerboard</span>
          </button>
          <button
            onClick={() => setMode("false_color")}
            className={`transition flex items-center space-x-1 cursor-pointer ${
              mode === "false_color"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            <Eye className="h-3 w-3" />
            <span>False Color RGB</span>
          </button>
        </div>
      </div>

      {/* Main View Area */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onTouchMove={handleTouchMove}
        className="image-stage relative w-full aspect-[4/3] max-h-[460px] rounded-xl select-none cursor-ew-resize"
      >
        {mode === "curtain" && (
          <>
            {/* Base layer: Reference image */}
            <img
              src={referenceImage}
              alt="Reference"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />

            {/* Overlap layer: Warped source image clipped by sliderPos */}
            <div
              className="absolute inset-0 overflow-hidden pointer-events-none"
              style={{ width: `${sliderPos}%` }}
            >
              <img
                src={warpedSourceImage}
                alt="Warped Source"
                className="absolute inset-0 w-full h-full object-contain max-w-none"
                style={{ width: containerRef.current?.clientWidth || "100%" }}
              />
            </div>

            {/* Divider Line */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-accent shadow-[0_0_12px_rgba(127,168,230,0.6)] pointer-events-none"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-7 w-7 rounded-full bg-base-deep border-2 border-accent flex items-center justify-center text-accent text-[10px] font-mono shadow-xl">
                ↔
              </div>
            </div>

            {/* Labels */}
            <div className="absolute top-3 left-3 text-[10px] font-mono px-2.5 py-1 rounded bg-base-deep/80 text-accent-strong border border-accent-line backdrop-blur pointer-events-none">
              WARPED SOURCE (REGISTERED)
            </div>
            <div className="absolute top-3 right-3 text-[10px] font-mono px-2.5 py-1 rounded bg-base-deep/80 text-warn border border-warn/30 backdrop-blur pointer-events-none">
              REFERENCE BASE
            </div>
          </>
        )}

        {mode === "diff" && (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={diffHeatmap}
              alt="Difference Heatmap"
              className="w-full h-full object-contain"
            />
            <div className="absolute top-3 left-3 text-[10px] font-mono px-2.5 py-1 rounded bg-base-deep/80 text-danger border border-danger/30 backdrop-blur">
              ABSOLUTE DIFFERENCE RESIDUAL (|I_REF - I_WARPED|)
            </div>
          </div>
        )}

        {mode === "checker" && (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={checkerboard}
              alt="Checkerboard Blend"
              className="w-full h-full object-contain"
            />
            <div className="absolute top-3 left-3 text-[10px] font-mono px-2.5 py-1 rounded bg-base-deep/80 text-accent-strong border border-accent-line backdrop-blur">
              CHECKERBOARD INTERLEAVING (8x8 TILES)
            </div>
          </div>
        )}

        {mode === "false_color" && (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={falseColor}
              alt="False Color Composite"
              className="w-full h-full object-contain"
            />
            <div className="absolute top-3 left-3 text-[10px] font-mono px-2.5 py-1 rounded bg-base-deep/80 text-warn border border-warn/30 backdrop-blur">
              FALSE COLOR (RED=SOURCE, GREEN=REF, YELLOW=MATCH)
            </div>
          </div>
        )}
      </div>

      <div className="text-[11px] font-mono text-muted flex items-center justify-between">
        <span>
          {mode === "curtain" && "Drag horizontally to compare continuous crater topography"}
          {mode === "diff" && "Inferno colormap: dark = perfect registration, bright = illumination/albedo differences"}
          {mode === "checker" && "Verify smooth crater edge continuity across alternating square tiles"}
          {mode === "false_color" && "Monochromatic yellow indicates sub-pixel alignment of lunar craters"}
        </span>
        <span className="text-dim hidden sm:inline">Sub-Pixel Warping: Bicubic Resampling</span>
      </div>
    </div>
  );
};
