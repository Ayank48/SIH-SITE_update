"use client";

import React, { useRef, useEffect, useState } from "react";
import { GraphTopology, GraphEdge } from "../../types";
import { Network, AlertTriangle } from "lucide-react";

interface CorrespondenceGraphProps {
  topology: GraphTopology;
  onSelectMatch: (matchId: number) => void;
}

export const CorrespondenceGraph: React.FC<CorrespondenceGraphProps> = ({ topology, onSelectMatch }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredEdge, setHoveredEdge] = useState<GraphEdge | null>(null);

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((event.clientY - rect.top) / rect.height) * canvas.height;
    let nearest = topology.nodes[0];
    let nearestDistance = Number.POSITIVE_INFINITY;
    for (const node of topology.nodes) {
      const px = 40 + (node.src_x - Math.min(...topology.nodes.map((n) => n.src_x), 0)) * Math.min((canvas.width - 80) / (Math.max(...topology.nodes.map((n) => n.src_x), 600) - Math.min(...topology.nodes.map((n) => n.src_x), 0) || 1), (canvas.height - 80) / (Math.max(...topology.nodes.map((n) => n.src_y), 600) - Math.min(...topology.nodes.map((n) => n.src_y), 0) || 1));
      const py = 40 + (node.src_y - Math.min(...topology.nodes.map((n) => n.src_y), 0)) * Math.min((canvas.width - 80) / (Math.max(...topology.nodes.map((n) => n.src_x), 600) - Math.min(...topology.nodes.map((n) => n.src_x), 0) || 1), (canvas.height - 80) / (Math.max(...topology.nodes.map((n) => n.src_y), 600) - Math.min(...topology.nodes.map((n) => n.src_y), 0) || 1));
      const distance = Math.hypot(x - px, y - py);
      if (distance < nearestDistance) { nearest = node; nearestDistance = distance; }
    }
    if (nearest && nearestDistance < 30) onSelectMatch(nearest.match_id);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || topology.nodes.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Find bounding box of nodes
    const xs = topology.nodes.map((n) => n.src_x);
    const ys = topology.nodes.map((n) => n.src_y);
    const minX = Math.min(...xs, 0);
    const maxX = Math.max(...xs, 600);
    const minY = Math.min(...ys, 0);
    const maxY = Math.max(...ys, 600);

    const pad = 40;
    const sourceNodeMap = new Map<number, { x: number; y: number }>();
    const referenceNodeMap = new Map<number, { x: number; y: number }>();
    const sourceMinX = minX;
    const sourceMinY = minY;
    const sourceMaxX = maxX;
    const sourceMaxY = maxY;
    const referenceXs = topology.nodes.map((n) => n.ref_x);
    const referenceYs = topology.nodes.map((n) => n.ref_y);
    const referenceMinX = Math.min(...referenceXs, 0);
    const referenceMinY = Math.min(...referenceYs, 0);
    const referenceMaxX = Math.max(...referenceXs, 600);
    const referenceMaxY = Math.max(...referenceYs, 600);
    const panelWidth = (width - 3 * pad) / 2;
    const sourceScale = Math.min(panelWidth / (sourceMaxX - sourceMinX || 1), (height - 2 * pad) / (sourceMaxY - sourceMinY || 1));
    const referenceScale = Math.min(panelWidth / (referenceMaxX - referenceMinX || 1), (height - 2 * pad) / (referenceMaxY - referenceMinY || 1));
    topology.nodes.forEach((n) => {
      sourceNodeMap.set(n.id, { x: pad + (n.src_x - sourceMinX) * sourceScale, y: pad + (n.src_y - sourceMinY) * sourceScale });
      referenceNodeMap.set(n.id, { x: 2 * pad + panelWidth + (n.ref_x - referenceMinX) * referenceScale, y: pad + (n.ref_y - referenceMinY) * referenceScale });
    });

    ctx.fillStyle = "#05070A";
    ctx.fillRect(pad - 10, pad - 10, panelWidth + 20, height - 2 * pad + 20);
    ctx.fillRect(2 * pad + panelWidth - 10, pad - 10, panelWidth + 20, height - 2 * pad + 20);

    // Draw Edges
    topology.edges.forEach((edge) => {
      const sourceP1 = sourceNodeMap.get(edge.source_node);
      const sourceP2 = sourceNodeMap.get(edge.target_node);
      const referenceP1 = referenceNodeMap.get(edge.source_node);
      const referenceP2 = referenceNodeMap.get(edge.target_node);
      if (!sourceP1 || !sourceP2 || !referenceP1 || !referenceP2) return;

      const isHovered =
        hoveredEdge &&
        hoveredEdge.source_node === edge.source_node &&
        hoveredEdge.target_node === edge.target_node;

      // Color by strain index
      let color = "#7FA8E6"; // Stable cyan
      if (edge.strain_index > 0.35) color = "#E0B45C"; // Moderate strain
      if (edge.strain_index > 0.65) color = "#E8737A"; // High strain

      for (const [p1, p2] of [[sourceP1, sourceP2], [referenceP1, referenceP2]]) {
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = isHovered ? "#FFFFFF" : color;
        ctx.lineWidth = isHovered ? 2.5 : edge.is_topologically_sound ? 1.0 : 1.5;
        ctx.globalAlpha = isHovered ? 1.0 : 0.7;
        ctx.stroke();
      }
    });

    // Draw Nodes
    ctx.globalAlpha = 1.0;
    topology.nodes.forEach((node) => {
      const sourceP = sourceNodeMap.get(node.id);
      const referenceP = referenceNodeMap.get(node.id);
      if (!sourceP || !referenceP) return;
      for (const p of [sourceP, referenceP]) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, 2 * Math.PI);
        ctx.fillStyle = "#A9C6F2";
        ctx.fill();
      }
      ctx.beginPath();
      ctx.moveTo(sourceP.x, sourceP.y);
      ctx.lineTo(referenceP.x, referenceP.y);
      ctx.strokeStyle = "rgba(169,198,242,0.18)";
      ctx.lineWidth = 0.6;
      ctx.stroke();
    });
  }, [topology, hoveredEdge]);

  return (
    <div className="panel-float p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-line pb-2">
        <div className="flex items-center space-x-2">
          <Network className="h-4 w-4 text-accent" />
            <span className="text-xs font-mono font-bold text-fg uppercase">
            RUNTIME CORRESPONDENCE DELAUNAY GRAPH
          </span>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-muted">
            NODES: <strong className="text-accent">{topology.nodes.length}</strong>
          </span>
          <span className="text-muted">
            EDGES: <strong className="text-accent">{topology.edges.length}</strong>
          </span>
          <span className="text-muted">
            INTEGRITY:{" "}
            <strong className="text-ok">
              {(topology.structural_integrity_score * 100).toFixed(1)}%
            </strong>
          </span>
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="image-stage technical-grid relative w-full aspect-[2/1] max-h-[460px] rounded-xl flex items-center justify-center">
        {topology.nodes.length < 4 && <div className="absolute inset-0 z-10 flex items-center justify-center text-xs font-mono text-muted">Insufficient correspondences for graph construction</div>}
        <canvas
          ref={canvasRef}
          width={1200}
          height={600}
          className="w-full h-full object-contain"
          onClick={handleCanvasClick}
        />

        {topology.topological_inversion_count > 0 && (
          <div className="absolute top-3 right-3 bg-warn/10 border border-warn/40 rounded-lg px-2.5 py-1 text-[11px] font-mono text-warn flex items-center space-x-1.5 backdrop-blur">
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>{topology.topological_inversion_count} local triangular relief strains</span>
          </div>
        )}
      </div>

      <div className="flex justify-between px-5 text-[10px] font-mono text-muted"><span>SOURCE INLIER GRAPH</span><span>REFERENCE INLIER GRAPH</span></div>

      <div className="flex items-center justify-between text-[11px] font-mono text-muted">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-accent"></span>
            <span>Rigid / Low Strain (&lt;35%)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-warn"></span>
            <span>Moderate edge strain</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="h-2 w-2 rounded-full bg-danger"></span>
            <span>High edge strain</span>
          </div>
        </div>
        <span className="text-dim hidden sm:inline">
          Mean edge strain: {topology.mean_strain.toFixed(3)}
        </span>
      </div>
    </div>
  );
};
