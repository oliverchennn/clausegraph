import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClauseGraph Verify — Evidence-backed financial planning",
  description: "Build an evidence-backed financial recovery plan, verify declared uncertainty bounds, and inspect the exact counterexample when it fails.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
