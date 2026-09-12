import React from "react";

const STEPS = [
  { n: "01", title: "Source Image", body: "OHRC / TMC-2 / IIRS / LRO NAC ingest, 8- or 16-bit TIFF and GeoTIFF." },
  { n: "02", title: "Preprocessing", body: "Radiometric normalisation, CLAHE, phase congruency or retinex, scale pyramid." },
  { n: "03", title: "Feature Representation", body: "SIFT / ORB / AKAZE keypoints, ANMS, SIFT-128 or CFOG descriptors." },
  { n: "04", title: "Correspondence Detection", body: "Coarse-to-fine descriptor matching with Lowe ratio test." },
  { n: "05", title: "Geometric Verification", body: "USAC-MAGSAC++ consensus, condition-guided homography vs. affine." },
  { n: "06", title: "Registration", body: "Sub-pixel bicubic warp, mosaic, checkerboard and false-colour blends." },
  { n: "07", title: "Accuracy Evaluation", body: "Transfer RMSE, inlier ratio, spatial entropy, NMI, SSIM." },
];

export const Workflow: React.FC = () => (
  <section id="workflow" className="relative py-20 lg:py-28 border-y border-line bg-navy/40">
    <div className="max-w-7xl mx-auto px-5 lg:px-8">
      <div className="max-w-2xl mb-14">
        <p className="eyebrow mb-3">Scientific workflow</p>
        <h2 className="text-3xl lg:text-4xl font-bold tracking-[-0.02em] text-fg">
          Seven stages from raw frame to verified registration
        </h2>
      </div>

      {/* Connected track */}
      <ol className="relative grid grid-cols-1 md:grid-cols-2 xl:grid-cols-7 gap-6 xl:gap-0">
        {/* Horizontal rail (desktop) */}
        <div className="hidden xl:block absolute left-0 right-0 top-[22px] h-px bg-gradient-to-r from-transparent via-line-strong to-transparent" />
        {/* Vertical rail (mobile) */}
        <div className="xl:hidden absolute left-[22px] top-0 bottom-0 w-px bg-line-strong md:hidden" />

        {STEPS.map((s, i) => (
          <li key={s.n} className="relative flex xl:flex-col gap-5 xl:gap-0 xl:px-3">
            <div className="relative z-10 shrink-0">
              <div className="h-11 w-11 rounded-full panel-float flex items-center justify-center metric text-[11px] text-accent-strong font-semibold">
                {s.n}
              </div>
              {i < STEPS.length - 1 && (
                <span className="hidden xl:block absolute top-1/2 -right-3 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-accent/60" />
              )}
            </div>
            <div className="xl:mt-6 pb-2">
              <h3 className="text-sm font-semibold text-fg tracking-tight">{s.title}</h3>
              <p className="mt-1.5 text-xs text-muted leading-relaxed">{s.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  </section>
);
