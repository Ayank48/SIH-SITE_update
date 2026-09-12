import React from "react";
import Link from "next/link";

export const Footer: React.FC = () => (
  <footer className="border-t border-line">
    <div className="max-w-7xl mx-auto px-5 lg:px-8 py-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div className="flex items-center gap-3">
        <div className="leading-tight">
          <div className="text-[13px] font-semibold text-fg">Chandrayaan-2 Optical Correspondence &amp; Registration Engine</div>
          <div className="text-[11px] text-dim font-mono mt-0.5">ISRO · Smart India Hackathon SIH26166 · Team ZeroDay</div>
        </div>
      </div>
      <div className="flex items-center gap-6 text-[12px] text-muted">
        <a href="#capabilities" className="hover:text-fg transition-colors">Capabilities</a>
        <a href="#workflow" className="hover:text-fg transition-colors">Workflow</a>
        <a href="#technology" className="hover:text-fg transition-colors">Technology</a>
        <Link href="/workspace" className="text-fg hover:text-accent-strong transition-colors">Workspace →</Link>
      </div>
    </div>
  </footer>
);
