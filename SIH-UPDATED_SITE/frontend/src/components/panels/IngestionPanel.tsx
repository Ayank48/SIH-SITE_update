"use client";

import React, { useRef, useState } from "react";
import { Upload, Database, CheckCircle2, Loader2, ImageIcon } from "lucide-react";
import { SamplePairInfo } from "../../types";

interface IngestionPanelProps {
  sourcePreview: string | null;
  referencePreview: string | null;
  sourceSensor: string;
  referenceSensor: string;
  sourceGsd: number;
  referenceGsd: number;
  sourceInfo?: { width: number; height: number; sensor: string };
  referenceInfo?: { width: number; height: number; sensor: string };
  onSensorChange: (role: "source" | "reference", sensor: string, gsd: number) => void;
  onFileUpload: (file: File, role: "source" | "reference") => void;
  onLoadSample: (sampleId: string) => void;
  samplePairs: SamplePairInfo[];
  isLoadingSample: boolean;
}

const SENSOR_OPTIONS = [
  { id: "OHRC", name: "Chandrayaan-2 OHRC", gsd: 0.25, badge: "0.25m PAN", desc: "Ultra-High Resolution" },
  { id: "TMC2", name: "Chandrayaan-2 TMC-2", gsd: 5.0, badge: "5.0m PAN", desc: "Stereo Mapping Camera" },
  { id: "IIRS", name: "Chandrayaan-2 IIRS", gsd: 80.0, badge: "80m SWIR", desc: "Hyperspectral Spectrometer" },
  { id: "LRO_NAC", name: "LRO NAC Reference", gsd: 0.5, badge: "0.5m PAN", desc: "Lunar Reconnaissance Orbiter" },
];

interface DropSlotProps {
  role: "source" | "reference";
  title: string;
  subtitle: string;
  tone: "accent" | "warn";
  preview: string | null;
  sensor: string;
  gsd: number;
  info?: { width: number; height: number; sensor: string };
  onSensorChange: (sensor: string, gsd: number) => void;
  onFile: (file: File) => void;
}

const DropSlot: React.FC<DropSlotProps> = ({
  role,
  title,
  subtitle,
  tone,
  preview,
  sensor,
  gsd,
  info,
  onSensorChange,
  onFile,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const toneText = tone === "accent" ? "text-accent" : "text-warn";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) onFile(e.target.files[0]);
  };

  return (
    <div className="panel-float p-4 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <span className={`dot ${toneText}`} />
          <div>
            <div className="text-xs font-semibold text-fg tracking-tight">{title}</div>
            <div className="label-sm">{subtitle}</div>
          </div>
        </div>
        {preview ? (
          <span className="chip text-ok border-ok/30 bg-ok/5">
            <CheckCircle2 className="h-3 w-3" /> Loaded
          </span>
        ) : (
          <span className="chip text-dim">Awaiting</span>
        )}
      </div>

      <div className="mb-3">
        <label className="label-sm block mb-1.5">Sensor payload &amp; GSD</label>
        <select
          value={sensor}
          onChange={(e) => {
            const opt = SENSOR_OPTIONS.find((s) => s.id === e.target.value);
            if (opt) onSensorChange(opt.id, opt.gsd);
          }}
          className="field"
        >
          {SENSOR_OPTIONS.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.badge})
            </option>
          ))}
        </select>
      </div>

      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        accept="image/*,.tif,.tiff"
        className="hidden"
      />
      <div
        role="button"
        tabIndex={0}
        aria-label={`Upload ${role} image`}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const f = e.dataTransfer.files?.[0];
          if (f) onFile(f);
        }}
        className={`dropzone image-stage h-48 flex flex-col items-center justify-center ${
          dragging ? "dropzone-active" : ""
        }`}
      >
        {preview ? (
          <>
            <img
              src={preview}
              alt={`${title} preview`}
              className="absolute inset-0 w-full h-full object-contain p-2 anim-fade"
            />
            <div className="absolute inset-x-0 bottom-0 p-2 flex items-center justify-between bg-gradient-to-t from-base-deep/90 to-transparent">
              <span className="chip !normal-case !tracking-normal text-fg-soft">
                <ImageIcon className="h-3 w-3" /> Replace image
              </span>
              {info && (
                <span className="text-[10px] font-mono text-fg-soft metric">
                  {info.width} × {info.height}
                </span>
              )}
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2 text-center px-4">
            <div className="h-11 w-11 rounded-2xl panel-inset flex items-center justify-center text-muted">
              <Upload className="h-5 w-5" />
            </div>
            <div className="text-xs text-fg-soft font-medium">
              Drop {role} image here or <span className={toneText}>browse</span>
            </div>
            <div className="text-[10px] font-mono text-dim">TIFF · GeoTIFF · PNG · JPEG (16/8-bit)</div>
          </div>
        )}
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-[10px] font-mono">
        <div className="panel-inset px-2.5 py-1.5">
          <div className="text-dim">SENSOR</div>
          <div className="text-fg-soft truncate">{info?.sensor ?? sensor}</div>
        </div>
        <div className="panel-inset px-2.5 py-1.5">
          <div className="text-dim">DIMS</div>
          <div className="text-fg-soft metric">{info ? `${info.width}×${info.height}` : "—"}</div>
        </div>
        <div className="panel-inset px-2.5 py-1.5">
          <div className="text-dim">GSD</div>
          <div className="text-fg-soft metric">{gsd} m/px</div>
        </div>
      </div>
    </div>
  );
};

export const IngestionPanel: React.FC<IngestionPanelProps> = ({
  sourcePreview,
  referencePreview,
  sourceSensor,
  referenceSensor,
  sourceGsd,
  referenceGsd,
  sourceInfo,
  referenceInfo,
  onSensorChange,
  onFileUpload,
  onLoadSample,
  samplePairs,
  isLoadingSample,
}) => {
  return (
    <div className="space-y-4">
      {/* Benchmark presets */}
      <div className="panel-float p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-lg panel-inset flex items-center justify-center text-accent">
              <Database className="h-3.5 w-3.5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-fg tracking-tight">Benchmark Lunar Test Pairs</h2>
              <p className="label-sm">Preloaded cross-sensor scenes</p>
            </div>
          </div>
          {isLoadingSample ? (
            <span className="chip text-accent border-accent-line bg-accent-soft">
              <Loader2 className="h-3 w-3 animate-spin" /> Loading
            </span>
          ) : (
            <span className="eyebrow hidden sm:block">Instant evaluation</span>
          )}
        </div>

        {samplePairs.length === 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[0, 1].map((i) => (
              <div key={i} className="h-[72px] rounded-xl skeleton border border-line" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {samplePairs.map((p) => (
              <button
                key={p.sample_id}
                onClick={() => onLoadSample(p.sample_id)}
                disabled={isLoadingSample}
                className="text-left p-3 rounded-xl panel-inset hover:border-accent-line hover:bg-accent-soft/40 transition-all duration-300 flex flex-col group cursor-pointer disabled:opacity-60 disabled:cursor-wait"
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="text-xs font-semibold text-fg group-hover:text-accent-strong transition-colors">
                    {p.title.split(":")[0]}
                  </span>
                  <span className="chip text-warn border-warn/30 bg-warn/5 !py-0">{p.sun_angle_delta}</span>
                </div>
                <p className="text-[11px] text-muted leading-relaxed line-clamp-2">{p.description}</p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Dual dropzones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DropSlot
          role="source"
          title="Source Image"
          subtitle="Search / moving"
          tone="accent"
          preview={sourcePreview}
          sensor={sourceSensor}
          gsd={sourceGsd}
          info={sourceInfo}
          onSensorChange={(s, g) => onSensorChange("source", s, g)}
          onFile={(f) => onFileUpload(f, "source")}
        />
        <DropSlot
          role="reference"
          title="Reference Image"
          subtitle="Base / fixed"
          tone="warn"
          preview={referencePreview}
          sensor={referenceSensor}
          gsd={referenceGsd}
          info={referenceInfo}
          onSensorChange={(s, g) => onSensorChange("reference", s, g)}
          onFile={(f) => onFileUpload(f, "reference")}
        />
      </div>
    </div>
  );
};
