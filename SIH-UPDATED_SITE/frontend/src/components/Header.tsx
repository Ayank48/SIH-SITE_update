"use client";

import React from "react";
import Link from "next/link";
import { Activity, Compass, ShieldCheck, ArrowLeft, Orbit } from "lucide-react";

interface HeaderProps {
  systemStatus: "online" | "offline";
  sessionId?: string;
  isProcessing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  systemStatus,
  sessionId,
  isProcessing,
}) => {
  const engineTone = isProcessing
    ? "text-warn"
    : systemStatus === "online"
    ? "text-ok"
    : "text-danger";

  return (
    <header className="glass-nav sticky top-0 z-50">
      <div className="max-w-[1700px] mx-auto px-4 lg:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-4 min-w-0">
          <Link
            href="/"
            className="hidden sm:inline-flex items-center gap-1.5 text-[11px] font-mono text-muted hover:text-fg transition-colors"
            aria-label="Back to overview"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Overview
          </Link>
          <span className="hidden sm:block h-5 w-px bg-line-strong" />
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-9 w-9 rounded-xl panel-inset flex items-center justify-center text-accent shrink-0">
              <Orbit className="h-4.5 w-4.5" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="eyebrow text-accent">ISRO / SIH26166</span>
                <span className="chip !py-0.5 text-warn border-warn/30 bg-warn/5">Team ZeroDay</span>
              </div>
              <h1 className="text-[13px] font-semibold tracking-tight text-fg truncate">
                Chandrayaan-2 Optical Correspondence &amp; Registration Engine
              </h1>
            </div>
          </div>
        </div>

        {/* Telemetry */}
        <div className="flex items-center gap-2 text-[11px] font-mono shrink-0">
          {sessionId && (
            <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg panel-inset text-muted">
              <Compass className="h-3.5 w-3.5 text-accent" />
              <span className="text-dim">SESSION</span>
              <span className="text-fg font-medium">{sessionId.slice(0, 8)}</span>
            </div>
          )}

          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg panel-inset">
            <span className={`dot ${engineTone} ${isProcessing ? "anim-pulse-soft" : ""}`} />
            <span className="text-dim">ENGINE</span>
            <span className={`font-medium ${engineTone}`}>
              {isProcessing ? "PROCESSING" : systemStatus.toUpperCase()}
            </span>
            {isProcessing && <Activity className="h-3.5 w-3.5 text-warn" />}
          </div>

          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg panel-inset text-muted">
            <ShieldCheck className="h-3.5 w-3.5 text-accent" />
            <span className="text-dim">ALGO</span>
            <span className="text-fg-soft">USAC-MAGSAC++ / SUB-PIXEL</span>
          </div>
        </div>
      </div>
    </header>
  );
};
