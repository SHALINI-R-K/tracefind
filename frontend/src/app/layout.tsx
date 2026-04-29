import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AmplifyProvider } from "@/contexts/identity_access/components/AmplifyProvider";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "TraceFind — AI-Powered Lost & Found",
  description:
    "Lose less. Find more. AI-driven item matching for campuses, offices, and public facilities.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans`}>
        <AmplifyProvider>{children}</AmplifyProvider>
      </body>
    </html>
  );
}
