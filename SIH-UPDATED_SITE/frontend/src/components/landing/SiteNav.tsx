"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export const SiteNav: React.FC = () => (
  <nav className="glass-nav sticky top-0 z-50">
    <div className="max-w-7xl mx-auto px-5 lg:px-8 h-16 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-3 group">
        <div className="leading-tight">
          <div className="eyebrow text-accent">ISRO / SIH26166</div>
          <div className="text-[13px] font-semibold tracking-tight text-fg">Lunar Correspondence Engine</div>
        </div>
      </Link>

      <div className="hidden md:flex items-center gap-7 text-[13px] text-muted">
        <a href="#capabilities" className="hover:text-fg transition-colors">Capabilities</a>
        <a href="#workflow" className="hover:text-fg transition-colors">Workflow</a>
        <a href="#technology" className="hover:text-fg transition-colors">Technology</a>
      </div>

      <Link href="/workspace" className="btn-ghost !py-2 !px-4 text-xs">
        Open Workspace <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  </nav>
);
