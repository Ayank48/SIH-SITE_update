"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { ArrowRight, Crosshair, Target, Sun } from "lucide-react";
import * as THREE from "three";

const LunarGlobe: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 100);
    camera.position.set(0, 0.08, 3.1);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.domElement.setAttribute("aria-label", "Interactive 3D lunar globe");
    renderer.domElement.className = "h-full w-full";
    mount.appendChild(renderer.domElement);

    const globe = new THREE.Group();
    scene.add(globe);

    const texture = new THREE.TextureLoader().load("/moon.png");
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    const moon = new THREE.Mesh(
      new THREE.SphereGeometry(1.05, 96, 96),
      new THREE.MeshStandardMaterial({
        map: texture,
        roughness: 0.92,
        metalness: 0.02,
        bumpMap: texture,
        bumpScale: 0.055,
      })
    );
    moon.castShadow = true;
    moon.receiveShadow = true;
    globe.add(moon);

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(1.075, 64, 64),
      new THREE.MeshBasicMaterial({
        color: 0x89a9d5,
        transparent: true,
        opacity: 0.065,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
      })
    );
    globe.add(atmosphere);

    const keyLight = new THREE.DirectionalLight(0xe8f0ff, 2.7);
    keyLight.position.set(-2.8, 1.8, 3.2);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x6d91c2, 1.2);
    rimLight.position.set(2.6, -1.2, -2.5);
    scene.add(rimLight);
    scene.add(new THREE.AmbientLight(0x26344b, 0.28));

    const resize = () => {
      if (!mount) return;
      const width = mount.clientWidth;
      const height = mount.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(mount);

    let animationFrame = 0;
    const animate = (time: number) => {
      globe.rotation.y = time * 0.000045;
      globe.rotation.x = Math.sin(time * 0.00018) * 0.025;
      renderer.render(scene, camera);
      animationFrame = requestAnimationFrame(animate);
    };
    animationFrame = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrame);
      resizeObserver.disconnect();
      texture.dispose();
      moon.geometry.dispose();
      moon.material.dispose();
      atmosphere.geometry.dispose();
      atmosphere.material.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return <div ref={mountRef} className="absolute inset-0" />;
};

export const Hero: React.FC = () => (
  <section className="relative overflow-hidden">
    {/* Lunar backdrop */}
    <div className="absolute inset-0 -z-10">
      <Image
        src="/lunar-surface.jpg"
        alt="Cratered lunar highlands photographed from orbit at low sun angle"
        fill
        priority
        sizes="100vw"
        className="object-cover object-center opacity-[0.22] saturate-[0.72] contrast-125"
      />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_68%_38%,transparent_0%,rgba(7,9,13,0.35)_44%,#07090d_82%)]" />
      <div className="absolute inset-0 bg-gradient-to-b from-[#07090d]/70 via-transparent to-[#07090d]" />
      <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-[#07090d] to-transparent" />
    </div>

    <div className="max-w-7xl mx-auto px-5 lg:px-8 pt-16 pb-20 lg:pt-24 lg:pb-28 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
      {/* Copy */}
      <div className="lg:col-span-6">
        <div className="chip text-accent border-accent-line bg-accent-soft mb-6 anim-rise">
          <span className="dot" /> Chandrayaan-2 · OHRC · TMC-2 · IIRS
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-[4.15rem] font-bold tracking-[-0.04em] leading-[1.02] text-fg anim-rise delay-1">
          Registering the Moon across every view.
        </h1>
        <p className="mt-6 text-base lg:text-lg text-muted leading-relaxed max-w-xl anim-rise delay-2">
          A scientific correspondence engine that aligns Chandrayaan-2 orbiter imagery across
          resolution, viewpoint and sun angle — with illumination-robust preprocessing,
          geometrically verified matching and quantitative accuracy evaluation.
        </p>
        <div className="mt-9 flex flex-wrap items-center gap-3 anim-rise delay-3">
          <Link href="/workspace" className="btn-primary">
            Open Workspace <ArrowRight className="h-4 w-4" />
          </Link>
          <a href="#workflow" className="btn-ghost">
            View the pipeline
          </a>
        </div>
        <div className="mt-10 grid grid-cols-3 gap-4 max-w-md anim-rise delay-4">
          {[
            ["0.25 m", "OHRC GSD"],
            ["320×", "Scale span OHRC→IIRS"],
            ["3×3", "Projective / affine models"],
          ].map(([v, l]) => (
            <div key={l}>
              <div className="metric text-xl font-semibold text-fg">{v}</div>
              <div className="label-sm mt-0.5">{l}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 3D lunar centerpiece */}
      <div className="lg:col-span-6 relative perspective-deep anim-fade delay-2">
        <div className="relative aspect-square max-w-[520px] mx-auto [transform-style:preserve-3d]">
          <div className="absolute inset-[12%] rounded-full bg-[radial-gradient(circle_at_35%_30%,rgba(196,214,239,0.14),transparent_45%)] blur-2xl" />
          <div className="absolute inset-[3%] rounded-full border border-accent/10 shadow-[0_0_90px_rgba(88,125,178,0.12)]" />
          {/* Orbital rings */}
          <div className="absolute inset-[6%] rounded-full border border-line anim-drift" />
          <div className="absolute inset-[-4%] rounded-full border border-dashed border-line anim-drift-reverse" />
          <div className="absolute left-1/2 top-[6%] -translate-x-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-accent-strong shadow-[0_0_14px_rgba(169,198,242,0.8)]" />

          {/* Moon */}
          <div className="absolute inset-[13%] anim-float [transform:translateZ(28px)]">
            <div className="absolute inset-[-8%] rounded-full bg-[#7899c7]/10 blur-2xl" />
            <LunarGlobe />
            <Image
              src="/moon.png"
              alt="The Moon"
              width={1024}
              height={1024}
              priority
              className="relative z-[-1] w-full h-full object-contain opacity-20 drop-shadow-[0_40px_80px_rgba(0,0,0,0.9)]"
            />
            {/* Crosshair overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute left-1/2 top-0 bottom-0 w-px bg-accent/20" />
              <div className="absolute top-1/2 left-0 right-0 h-px bg-accent/20" />
              <div className="absolute left-[38%] top-[42%] h-6 w-6 -translate-x-1/2 -translate-y-1/2 border border-accent-strong/70 rounded-sm">
                <span className="absolute -right-1 -top-1 h-1.5 w-1.5 bg-accent-strong rounded-full" />
              </div>
            </div>
          </div>

          {/* Floating glass panels */}
          <div className="absolute -left-2 sm:-left-6 top-[18%] panel-float px-4 py-3 anim-float tilt-card">
            <div className="flex items-center gap-2 label-sm mb-1">
              <Target className="h-3 w-3 text-accent" /> Transfer RMSE
            </div>
            <div className="metric text-lg font-semibold text-fg">Target: &lt; 1.0 <span className="text-xs text-muted">px</span></div>
            <div className="text-[10px] font-mono text-ok">registration objective</div>
          </div>

          <div className="absolute -right-2 sm:-right-6 top-[44%] panel-float px-4 py-3 anim-float-delayed">
            <div className="flex items-center gap-2 label-sm mb-1">
              <Crosshair className="h-3 w-3 text-accent" /> Verification
            </div>
            <div className="text-sm font-semibold text-fg">Robust geometric verification</div>
            <div className="text-[10px] font-mono text-muted">USAC-MAGSAC++ capability</div>
          </div>

          <div className="absolute left-[14%] bottom-[4%] panel-float px-4 py-3 anim-float">
            <div className="flex items-center gap-2 label-sm mb-1">
              <Sun className="h-3 w-3 text-warn" /> Illumination
            </div>
            <div className="text-sm font-semibold text-fg">Sun-angle robust</div>
            <div className="text-[10px] font-mono text-muted">CLAHE · phase congruency · retinex</div>
          </div>

          <div className="absolute right-[11%] bottom-[7%] panel-float hidden sm:block px-3 py-2 anim-float-delayed">
            <div className="eyebrow text-accent mb-1">Mission geometry</div>
            <div className="metric text-xs text-fg-soft">OHRC → TMC-2</div>
            <div className="text-[10px] font-mono text-dim">cross-sensor alignment</div>
          </div>
        </div>
      </div>
    </div>
  </section>
);
