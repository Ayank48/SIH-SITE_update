import React from "react";

const SENSORS = [
  { id: "OHRC", name: "Chandrayaan-2 OHRC", spec: "0.25 m PAN", note: "Orbiter High Resolution Camera" },
  { id: "TMC-2", name: "Chandrayaan-2 TMC-2", spec: "5.0 m PAN", note: "Terrain Mapping Camera" },
  { id: "IIRS", name: "Chandrayaan-2 IIRS", spec: "80 m SWIR", note: "Imaging IR Spectrometer" },
  { id: "NAC", name: "LRO NAC", spec: "0.5 m PAN", note: "Reference cross-mission" },
];

const STACK = [
  ["Correspondence", "OpenCV (contrib), SIFT / ORB / AKAZE, CFOG, ANMS"],
  ["Verification", "USAC-MAGSAC++, RANSAC, condition-number gating"],
  ["Evaluation", "scikit-image SSIM, NMI, spatial entropy, Delaunay topology (SciPy / NetworkX)"],
  ["Ingestion", "tifffile, Pillow, NumPy — 8/16-bit TIFF, GeoTIFF, PNG, JPEG"],
  ["Service", "FastAPI + Uvicorn backend, Next.js analysis workspace"],
  ["Assurance", "Lunar Court verdicts, DNA certificate, blind audit, pytest suite"],
];

export const Technology: React.FC = () => (
  <section id="technology" className="max-w-7xl mx-auto px-5 lg:px-8 py-20 lg:py-28">
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
      <div className="lg:col-span-5">
        <p className="eyebrow mb-3">Sensor ecosystem</p>
        <h2 className="text-3xl lg:text-4xl font-bold tracking-[-0.02em] text-fg">
          Trusted instruments, one registration frame
        </h2>
        <p className="mt-4 text-muted leading-relaxed">
          The engine models each payload&apos;s ground sampling distance so scale ratios are
          physically grounded, and can operate blind — inferring scale and rotation without metadata.
        </p>

        <div className="mt-8 grid grid-cols-2 gap-3">
          {SENSORS.map((s) => (
            <div key={s.id} className="panel panel-hover p-4">
              <div className="flex items-center justify-between">
                <span className="metric text-sm font-semibold text-fg">{s.id}</span>
                <span className="chip !py-0 text-accent border-accent-line bg-accent-soft">{s.spec}</span>
              </div>
              <div className="mt-2 text-xs text-fg-soft">{s.name}</div>
              <div className="text-[10px] font-mono text-dim mt-0.5">{s.note}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:col-span-7">
        <div className="panel-float p-6 lg:p-8 h-full">
          <div className="flex items-center justify-between mb-6">
            <p className="eyebrow">Technology stack</p>
            <span className="chip text-ok border-ok/30 bg-ok/5"><span className="dot" /> Deterministic</span>
          </div>
          <dl className="divide-y divide-line">
            {STACK.map(([k, v]) => (
              <div key={k} className="grid grid-cols-1 sm:grid-cols-12 gap-1 sm:gap-6 py-4 first:pt-0 last:pb-0">
                <dt className="sm:col-span-3 label-sm text-fg-soft">{k}</dt>
                <dd className="sm:col-span-9 text-sm text-muted leading-relaxed">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  </section>
);
