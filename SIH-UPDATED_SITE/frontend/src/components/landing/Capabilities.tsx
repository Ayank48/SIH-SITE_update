import React from "react";
import { Layers, Sun, Maximize2, Move3d, Gauge } from "lucide-react";

const ITEMS = [
  {
    icon: Layers,
    title: "Multi-modal Image Correspondence",
    body:
      "Finds corresponding points between panchromatic OHRC and TMC-2 frames and SWIR IIRS data, using SIFT, ORB or AKAZE keypoints with adaptive non-maximal suppression for even coverage.",
    tag: "SIFT · ORB · AKAZE · ANMS",
  },
  {
    icon: Sun,
    title: "Sun-Angle Robust Matching",
    body:
      "Illumination normalisation via CLAHE, phase congruency or multi-scale retinex, with orientation-modulo CFOG descriptors that stay stable when shadows flip between passes.",
    tag: "CLAHE · Phase Congruency · CFOG",
  },
  {
    icon: Maximize2,
    title: "Scale & Viewpoint Robustness",
    body:
      "Scale-space pyramids and coarse-to-fine matching bridge the 0.25 m to 80 m resolution gap, while ratio-test filtering removes ambiguous descriptor pairs.",
    tag: "Scale pyramid · Lowe ratio",
  },
  {
    icon: Move3d,
    title: "Precise Image Registration",
    body:
      "Homography or affine models are estimated with USAC-MAGSAC++, conditioned for numerical stability, then applied with bicubic sub-pixel warping into the reference frame.",
    tag: "USAC-MAGSAC++ · Bicubic warp",
  },
  {
    icon: Gauge,
    title: "Match Quality & Evaluation",
    body:
      "Transfer RMSE, inlier count and ratio, spatial entropy and grid coverage, plus post-registration NMI and SSIM — every run is reported with its full transformation matrix.",
    tag: "RMSE · Inliers · NMI · SSIM",
  },
];

export const Capabilities: React.FC = () => (
  <section id="capabilities" className="max-w-7xl mx-auto px-5 lg:px-8 py-20 lg:py-28">
    <div className="max-w-2xl mb-12">
      <p className="eyebrow mb-3">Capabilities</p>
      <h2 className="text-3xl lg:text-4xl font-bold tracking-[-0.02em] text-fg">
        Built for the physics of lunar imagery
      </h2>
      <p className="mt-4 text-muted leading-relaxed">
        Low-texture regolith, long crater shadows and a 320× spread in ground sampling distance
        break generic feature matchers. Each stage of the engine is designed around those constraints.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {ITEMS.map((it, i) => (
        <article
          key={it.title}
          className={`panel panel-hover p-6 flex flex-col ${i === 0 ? "xl:col-span-2 xl:flex-row xl:items-start xl:gap-8" : ""}`}
        >
          <div className="h-10 w-10 rounded-xl panel-inset flex items-center justify-center text-accent shrink-0 mb-5 xl:mb-0">
            <it.icon className="h-4.5 w-4.5" />
          </div>
          <div className="flex-1">
            <h3 className="text-base font-semibold text-fg tracking-tight">{it.title}</h3>
            <p className="mt-2 text-sm text-muted leading-relaxed">{it.body}</p>
            <div className="mt-4 label-sm text-accent/80">{it.tag}</div>
          </div>
        </article>
      ))}
    </div>
  </section>
);
