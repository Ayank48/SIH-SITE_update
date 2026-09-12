import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { SiteNav } from "../components/landing/SiteNav";
import { Hero } from "../components/landing/Hero";
import { Capabilities } from "../components/landing/Capabilities";
import { Workflow } from "../components/landing/Workflow";
import { Technology } from "../components/landing/Technology";
import { Footer } from "../components/landing/Footer";

export default function WelcomePage() {
  return (
    <div className="min-h-screen flex flex-col text-fg">
      <SiteNav />
      <main className="flex-1">
        <Hero />
        <Capabilities />
        <Workflow />
        <Technology />

        {/* Closing CTA */}
        <section className="max-w-7xl mx-auto px-5 lg:px-8 pb-24">
          <div className="panel-float p-8 lg:p-12 flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden">
            <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full border border-line anim-drift" />
            <div>
              <p className="eyebrow mb-2">Ready when you are</p>
              <h2 className="text-2xl lg:text-3xl font-bold tracking-[-0.02em] text-fg">
                Load a benchmark pair and run the pipeline.
              </h2>
              <p className="mt-2 text-muted max-w-lg">
                Preloaded OHRC / TMC-2 scenes let you inspect correspondence vectors, blended mosaics and full telemetry in seconds.
              </p>
            </div>
            <Link href="/workspace" className="btn-primary shrink-0">
              Open Workspace <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
