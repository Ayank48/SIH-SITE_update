"use client";

import React, { useRef, useState, useEffect } from "react";
import { MatchPoint } from "../../types";

interface DualViewportProps {
  sourceImage: string | null;
  referenceImage: string | null;
  matches: MatchPoint[];
  sourceDimensions?: { width: number; height: number };
  referenceDimensions?: { width: number; height: number };
}

export const DualViewport: React.FC<DualViewportProps> = ({
  sourceImage,
  referenceImage,
  matches,
  sourceDimensions,
  referenceDimensions,
}) => {
  const [filterMode, setFilterMode] = useState<"all" | "inliers" | "court_accept" | "outliers">("inliers");
  const [hoveredMatch, setHoveredMatch] = useState<MatchPoint | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const filteredMatches = matches.filter((m) => {
    if (filterMode === "inliers") return m.is_inlier;
    if (filterMode === "outliers") return !m.is_inlier;
    if (filterMode === "court_accept") return m.verdict === "ACCEPT";
    return true;
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !sourceImage || !referenceImage) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img1 = new Image();
    const img2 = new Image();

    let loaded = 0;
    const onLoad = () => {
      loaded++;
      if (loaded === 2) {
        renderCanvas(ctx, img1, img2);
      }
    };

    img1.onload = onLoad;
    img2.onload = onLoad;
    img1.src = sourceImage;
    img2.src = referenceImage;
  }, [sourceImage, referenceImage, filteredMatches, hoveredMatch]);

  const renderCanvas = (
    ctx: CanvasRenderingContext2D,
    img1: HTMLImageElement,
    img2: HTMLImageElement
  ) => {
    const canvas = ctx.canvas;
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Draw Source on left half, Reference on right half
    const halfW = width / 2;
    const gap = 4;

    const scale1 = Math.min((halfW - gap) / img1.width, height / img1.height);
    const scale2 = Math.min((halfW - gap) / img2.width, height / img2.height);

    const w1 = img1.width * scale1;
    const h1 = img1.height * scale1;
    const x1 = (halfW - gap - w1) / 2;
    const y1 = (height - h1) / 2;

    const w2 = img2.width * scale2;
    const h2 = img2.height * scale2;
    const x2 = halfW + gap + (halfW - gap - w2) / 2;
    const y2 = (height - h2) / 2;

    // Background dark panels
    ctx.fillStyle = "#05070A";
    ctx.fillRect(0, 0, halfW - gap, height);
    ctx.fillRect(halfW + gap, 0, halfW - gap, height);

    // Draw images
    ctx.drawImage(img1, x1, y1, w1, h1);
    ctx.drawImage(img2, x2, y2, w2, h2);

    // Center divider
    ctx.strokeStyle = "#1A212C";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(halfW, 0);
    ctx.lineTo(halfW, height);
    ctx.stroke();

    // Draw matches
    filteredMatches.forEach((m) => {
      const sx = x1 + m.src_x * scale1;
      const sy = y1 + m.src_y * scale1;
      const rx = x2 + m.ref_x * scale2;
      const ry = y2 + m.ref_y * scale2;

      const isHovered = hoveredMatch && hoveredMatch.id === m.id;

      // Color logic based on verdict and inlier status
      let strokeColor = "#6FCF97"; // Inlier green
      if (m.verdict === "ACCEPT") strokeColor = "#7FA8E6"; // Court accept cyan
      else if (m.verdict === "UNCERTAIN") strokeColor = "#E0B45C"; // Uncertain amber
      else if (m.verdict === "REJECT" || !m.is_inlier) strokeColor = "#E8737A"; // Outlier red

      // Draw vector correspondence line
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(rx, ry);
      ctx.strokeStyle = isHovered ? "#FFFFFF" : strokeColor;
      ctx.lineWidth = isHovered ? 2.5 : 1.0;
      ctx.globalAlpha = isHovered ? 1.0 : 0.65;
      ctx.stroke();

      // Source keypoint marker
      ctx.beginPath();
      ctx.arc(sx, sy, isHovered ? 4.5 : 2.5, 0, 2 * Math.PI);
      ctx.fillStyle = isHovered ? "#FFFFFF" : strokeColor;
      ctx.fill();

      // Ref keypoint marker
      ctx.beginPath();
      ctx.arc(rx, ry, isHovered ? 4.5 : 2.5, 0, 2 * Math.PI);
      ctx.fillStyle = isHovered ? "#FFFFFF" : strokeColor;
      ctx.fill();
    });

    ctx.globalAlpha = 1.0;
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || filteredMatches.length === 0) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * canvas.width;
    const mouseY = ((e.clientY - rect.top) / rect.height) * canvas.height;

    const width = canvas.width;
    const height = canvas.height;
    const halfW = width / 2;
    const gap = 4;

    // Check keypoints on both sides
    let nearest: MatchPoint | null = null;
    let minDist = 18.0;

    const sourceWidth = sourceDimensions?.width ?? 600;
    const sourceHeight = sourceDimensions?.height ?? 600;
    const referenceWidth = referenceDimensions?.width ?? 600;
    const referenceHeight = referenceDimensions?.height ?? 600;
    const sourceScale = Math.min((halfW - gap) / sourceWidth, height / sourceHeight);
    const referenceScale = Math.min((halfW - gap) / referenceWidth, height / referenceHeight);
    const x1 = (halfW - gap - sourceWidth * sourceScale) / 2;
    const y1 = (height - sourceHeight * sourceScale) / 2;
    const x2 = halfW + gap + (halfW - gap - referenceWidth * referenceScale) / 2;
    const y2 = (height - referenceHeight * referenceScale) / 2;

    for (const m of filteredMatches) {
      const sx = x1 + m.src_x * sourceScale;
      const sy = y1 + m.src_y * sourceScale;
      const rx = x2 + m.ref_x * referenceScale;
      const ry = y2 + m.ref_y * referenceScale;

      const d_src = Math.hypot(mouseX - sx, mouseY - sy);
      const d_ref = Math.hypot(mouseX - rx, mouseY - ry);
      const d = Math.min(d_src, d_ref);

      if (d < minDist) {
        minDist = d;
        nearest = m;
      }
    }

    setHoveredMatch(nearest);
  };

  return (
    <div className="panel-float p-4 space-y-3">
      {/* Viewport Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono font-bold text-fg uppercase">
            DUAL-VIEWPORT CORRESPONDENCE VECTOR CANVAS
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-soft text-accent-strong border border-accent-line">
            {filteredMatches.length} / {matches.length} matches
          </span>
        </div>

        {/* Filter Buttons */}
        <div className="seg">
          <button
            onClick={() => setFilterMode("inliers")}
            className={`transition cursor-pointer ${
              filterMode === "inliers"
                ? "seg-active text-ok"
                : "seg-idle"
            }`}
          >
            Inliers
          </button>
          <button
            onClick={() => setFilterMode("court_accept")}
            className={`transition cursor-pointer ${
              filterMode === "court_accept"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            Court Accept
          </button>
          <button
            onClick={() => setFilterMode("outliers")}
            className={`transition cursor-pointer ${
              filterMode === "outliers"
                ? "seg-active text-danger"
                : "seg-idle"
            }`}
          >
            Outliers
          </button>
          <button
            onClick={() => setFilterMode("all")}
            className={`transition cursor-pointer ${
              filterMode === "all"
                ? "seg-active"
                : "seg-idle"
            }`}
          >
            All
          </button>
        </div>
      </div>

      {/* Interactive Canvas */}
      <div className="image-stage technical-grid relative w-full aspect-[2/1] max-h-[460px] rounded-xl">
        <canvas
          ref={canvasRef}
          width={1200}
          height={600}
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={() => setHoveredMatch(null)}
          className="w-full h-full object-contain cursor-crosshair"
        />

        {/* Labels Overlay */}
        <div className="absolute top-2 left-3 pointer-events-none text-[10px] font-mono px-2 py-0.5 rounded bg-base-deep/80 backdrop-blur text-accent-strong border border-accent-line">
          SOURCE IMAGE (OHRC / INPUT)
        </div>
        <div className="absolute top-2 right-3 pointer-events-none text-[10px] font-mono px-2 py-0.5 rounded bg-base-deep/80 backdrop-blur text-warn border border-warn/30">
          REFERENCE IMAGE (TMC-2 / BASE)
        </div>

        {/* Hover Tooltip Card */}
        {hoveredMatch && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 panel-float px-3.5 py-2 shadow-2xl backdrop-blur font-mono text-xs pointer-events-none flex items-center space-x-4">
            <div>
              <span className="text-[10px] text-muted block">SOURCE COORD:</span>
              <span className="text-accent font-bold">
                ({hoveredMatch.src_x}, {hoveredMatch.src_y})
              </span>
            </div>
            <div className="h-6 w-px bg-line-strong"></div>
            <div>
              <span className="text-[10px] text-muted block">REF COORD:</span>
              <span className="text-warn font-bold">
                ({hoveredMatch.ref_x}, {hoveredMatch.ref_y})
              </span>
            </div>
            <div className="h-6 w-px bg-line-strong"></div>
            <div>
              <span className="text-[10px] text-muted block">LUNAR COURT:</span>
              <span
                className={`font-bold ${
                  hoveredMatch.verdict === "ACCEPT"
                    ? "text-ok"
                    : hoveredMatch.verdict === "UNCERTAIN"
                    ? "text-warn"
                    : "text-danger"
                }`}
              >
                {hoveredMatch.verdict} ({(hoveredMatch.confidence * 100).toFixed(0)}%)
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="flex items-center justify-between text-[11px] font-mono text-muted pt-1">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-accent"></span>
            <span>Court Accepted Inlier</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-warn"></span>
            <span>Uncertain / Borderline</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-danger"></span>
            <span>Rejected Geometric Outlier</span>
          </div>
        </div>
        <span className="text-dim hidden sm:inline">Hover over points to inspect physical coordinates</span>
      </div>
    </div>
  );
};
