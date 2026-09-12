import type { Metadata } from "next";
import { Manrope, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Lunar Correspondence & Registration Engine | Chandrayaan-2",
  description:
    "Multi-modal lunar image correspondence and sub-pixel registration for Chandrayaan-2 OHRC, TMC-2 and IIRS imagery. Sun-angle robust matching, geometric verification and quantitative evaluation.",
  openGraph: {
    title: "Lunar Correspondence & Registration Engine",
    description:
      "Scientific platform for cross-sensor lunar image correspondence, geometric verification and registration accuracy evaluation.",
    type: "website",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${manrope.variable} ${plexMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col scene">{children}</body>
    </html>
  );
}
