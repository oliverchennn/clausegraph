import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClauseGraph — Your financial recovery workspace",
  description: "Understand the fine print. Protect the essentials. Build an evidence-backed financial recovery plan.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
