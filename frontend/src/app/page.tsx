import Link from "next/link";
import { Search, Sparkles, Bell, ShieldCheck } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

const features = [
  {
    icon: Search,
    title: "Smart Matching",
    description: "AI compares images and text descriptions to find your items automatically.",
  },
  {
    icon: Sparkles,
    title: "Instant Embeddings",
    description: "Powered by AWS Bedrock Titan for real-time image and text similarity scoring.",
  },
  {
    icon: Bell,
    title: "Real-time Alerts",
    description: "Get notified instantly when a potential match for your lost item is found.",
  },
  {
    icon: ShieldCheck,
    title: "Secure Claims",
    description: "Two-party confirmation flow ensures items reach the right owner every time.",
  },
];

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background gradient orbs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-primary/20 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute left-1/2 top-1/3 h-60 w-60 -translate-x-1/2 rounded-full bg-primary/5 blur-[100px]" />
      </div>

      {/* Hero */}
      <main className="relative mx-auto max-w-5xl px-6 pt-24 pb-20">
        <div className="flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm text-primary mb-8">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Recovery
          </div>

          <h1 className="max-w-3xl text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            Lose less.{" "}
            <span className="bg-gradient-to-r from-primary via-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Find more.
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
            TraceFind uses AI-driven image and text embeddings to automatically match lost items
            with found reports across campuses, offices, and public facilities.
          </p>

          <div className="mt-10 flex gap-4">
            <Button size="lg" asChild>
              <Link href="/dashboard">Get started</Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link href="/dashboard/report">Report an item</Link>
            </Button>
          </div>
        </div>

        {/* Features grid */}
        <div className="mt-28 grid gap-6 sm:grid-cols-2">
          {features.map((f) => (
            <div
              key={f.title}
              className="group relative rounded-xl border bg-card/50 backdrop-blur-sm p-6 transition-all duration-300 hover:border-primary/40 hover:bg-card/80 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-2.5 text-primary transition-colors group-hover:bg-primary/20">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {f.description}
              </p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <footer className="mt-28 border-t pt-8 text-center text-sm text-muted-foreground">
          TraceFind © {new Date().getFullYear()} — Smart Lost &amp; Found System
        </footer>
      </main>
    </div>
  );
}
