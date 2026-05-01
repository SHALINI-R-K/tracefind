import Link from "next/link";
import {
  ArrowUpRight,
  Search,
  Sparkles,
  Bell,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";

const stats = [
  { n: "0.70", label: "Cosine threshold" },
  { n: "<2s", label: "API latency p95" },
  { n: "1024", label: "Embedding dimensions" },
];

const features = [
  {
    n: "01",
    icon: Search,
    title: "Smart Matching",
    body: "Cosine similarity over Bedrock Titan v2 text embeddings, blended with Groq Vision captions of the original photograph.",
  },
  {
    n: "02",
    icon: Sparkles,
    title: "Real-Time Pipeline",
    body: "DynamoDB Streams trigger matching the instant an item is reported. No polling, no cron jobs, no waiting.",
  },
  {
    n: "03",
    icon: Bell,
    title: "Idempotent Notifications",
    body: "Both parties receive in-app and SMTP email alerts. Deterministic IDs deduplicate retries — never two emails for one match.",
  },
  {
    n: "04",
    icon: ShieldCheck,
    title: "Atomic Claims",
    body: "TransactWriteItems locks both items in a single DynamoDB transaction. Race-free, double-claim-proof, audited.",
  },
];

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Ambient grid backdrop — kept very subtle */}
      <div
        className="pointer-events-none fixed inset-0 grid-overlay opacity-[0.18]"
        aria-hidden
      />

      {/* Masthead */}
      <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 pt-10 pb-6 md:px-12">
        <Link
          href="/"
          className="flex items-baseline gap-2.5 text-lg font-semibold tracking-tight"
        >
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
            <Search className="h-3.5 w-3.5" strokeWidth={2.25} />
          </span>
          <span>TraceFind</span>
          <span className="ml-1 hidden font-mono text-[0.65rem] uppercase tracking-[0.25em] text-muted-foreground sm:inline">
            v0.1
          </span>
        </Link>

        <nav className="flex items-center gap-1 text-sm">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/signin">Sign in</Link>
          </Button>
          <Button size="sm" asChild>
            <Link href="/signup">
              Sign up
              <ArrowUpRight className="ml-1.5 h-3.5 w-3.5" />
            </Link>
          </Button>
        </nav>
      </header>

      <div className="rule-double mx-auto max-w-6xl px-6 md:px-12" />

      {/* HERO */}
      <section className="relative mx-auto max-w-6xl px-6 pt-16 pb-20 md:px-12 md:pt-24 md:pb-28">
        <div className="grid gap-12 md:grid-cols-12">
          <div className="md:col-span-8">
            <div
              className="mb-7 flex items-center gap-3 opacity-0 animate-fade-in-up"
              style={{ animationDelay: "60ms" }}
            >
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 text-[0.7rem] font-medium uppercase tracking-[0.22em] text-primary">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                  <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-primary" />
                </span>
                AI-powered recovery
              </span>
              <span className="hidden h-px flex-1 bg-gradient-to-r from-border to-transparent sm:block" />
              <span className="hidden font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground sm:inline">
                v0.1
              </span>
            </div>

            <h1
              className="
                font-display font-bold leading-[0.92] tracking-tight text-foreground
                text-[clamp(3rem,9vw,7.5rem)]
                opacity-0 animate-fade-in-up
              "
              style={{ animationDelay: "180ms" }}
            >
              Lose
              <br />
              <span className="underline-accent">less.</span>
              <br />
              <span
                className="bg-clip-text text-transparent"
                style={{
                  backgroundImage:
                    "linear-gradient(110deg, hsl(var(--aurora-1)) 0%, hsl(var(--aurora-2)) 45%, hsl(var(--aurora-1)) 100%)",
                }}
              >
                Find&nbsp;more.
              </span>
            </h1>

            <p
              className="
                mt-10 max-w-xl text-lg leading-relaxed text-muted-foreground md:text-xl
                opacity-0 animate-fade-in-up
              "
              style={{ animationDelay: "440ms" }}
            >
              TraceFind uses AI-driven image and text embeddings to automatically
              match lost items with found reports across campuses, offices, and
              public facilities.
            </p>

            <div
              className="mt-10 flex flex-wrap items-center gap-3 opacity-0 animate-fade-in-up"
              style={{ animationDelay: "640ms" }}
            >
              <Button size="lg" asChild>
                <Link href="/signup">
                  Get started
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/signin">Sign in</Link>
              </Button>
            </div>
          </div>

          {/* Side rail — running figures, with crosshair decoration */}
          <aside className="relative md:col-span-4 md:pl-8 md:border-l md:border-border">
            {/* Top crosshair — calls back to the "find / locate" theme */}
            <svg
              aria-hidden
              className="absolute -left-[7px] -top-2 h-3.5 w-3.5 text-primary"
              viewBox="0 0 14 14"
            >
              <path
                d="M7 0v4M7 10v4M0 7h4M10 7h4"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
              />
              <circle
                cx="7"
                cy="7"
                r="1.5"
                fill="currentColor"
              />
            </svg>

            <p className="mb-6 font-mono text-[0.65rem] uppercase tracking-[0.28em] text-muted-foreground">
              Running figures
            </p>
            <dl className="space-y-7">
              {stats.map((s, i) => (
                <div
                  key={s.label}
                  className="group opacity-0 animate-fade-in-up"
                  style={{ animationDelay: `${750 + i * 110}ms` }}
                >
                  <dt className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
                    {s.label}
                  </dt>
                  <dd className="index-number mt-1 text-5xl leading-none">
                    <span
                      className="bg-clip-text text-transparent"
                      style={{
                        backgroundImage:
                          "linear-gradient(180deg, hsl(var(--foreground)) 0%, hsl(var(--foreground) / 0.7) 100%)",
                      }}
                    >
                      {s.n}
                    </span>
                  </dd>
                </div>
              ))}
            </dl>

            {/* Bottom crosshair */}
            <svg
              aria-hidden
              className="absolute -left-[7px] bottom-0 h-3.5 w-3.5 text-primary/40"
              viewBox="0 0 14 14"
            >
              <path
                d="M7 0v4M7 10v4M0 7h4M10 7h4"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
              />
            </svg>
          </aside>
        </div>
      </section>

      <div className="rule-double mx-auto max-w-6xl px-6 md:px-12" />

      {/* PILLARS */}
      <section className="relative mx-auto max-w-6xl px-6 py-20 md:px-12 md:py-28">
        <p className="mb-2 font-mono text-xs uppercase tracking-[0.28em] text-muted-foreground">
          The pipeline
        </p>
        <h2 className="font-display text-4xl font-bold leading-tight tracking-tight md:text-5xl">
          From report to reunion in four steps.
        </h2>

        <div className="mt-14 grid gap-x-8 gap-y-12 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <article
              key={f.n}
              className="group relative border-t border-border pt-7 opacity-0 animate-fade-in-up"
              style={{ animationDelay: `${100 + i * 80}ms` }}
            >
              <div className="absolute -top-px left-0 h-px w-12 bg-primary transition-[width] duration-500 ease-ink group-hover:w-24" />
              <div className="flex items-start justify-between">
                <span className="index-number text-2xl text-muted-foreground">
                  {f.n}
                </span>
                <span className="rounded-md border border-border bg-card p-2 text-primary">
                  <f.icon className="h-4 w-4" strokeWidth={1.75} />
                </span>
              </div>
              <h3 className="mt-5 font-display text-lg font-semibold leading-snug tracking-tight">
                {f.title}
              </h3>
              <p className="mt-3 text-[0.9rem] leading-relaxed text-muted-foreground">
                {f.body}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="relative mx-auto max-w-4xl px-6 py-20 md:px-12 md:py-28">
        <div
          className="
            relative overflow-hidden rounded-lg border border-border bg-card
            px-8 py-12 text-center md:px-16 md:py-20
          "
        >
          {/* Glow accent */}
          <div
            className="pointer-events-none absolute inset-x-0 -top-32 mx-auto h-64 w-2/3 rounded-full bg-primary/20 blur-[100px]"
            aria-hidden
          />
          <div className="relative">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted-foreground">
              Ready when you are
            </p>
            <h2 className="mt-4 font-display text-4xl font-bold leading-tight tracking-tight md:text-5xl">
              Report your first item.
            </h2>
            <p className="mx-auto mt-4 max-w-md text-muted-foreground">
              Ninety seconds. The matcher starts comparing the moment you submit.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Button size="lg" asChild>
                <Link href="/signup">
                  Create account
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="ghost" size="lg" asChild>
                <Link href="/signin">Already have an account? Sign in</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Colophon */}
      <footer className="relative mx-auto max-w-6xl px-6 pb-12 md:px-12">
        <div className="rule-double mb-8" />
        <div className="flex flex-wrap items-center justify-between gap-3 font-mono text-[0.65rem] uppercase tracking-[0.28em] text-muted-foreground">
          <span>TraceFind &copy; {new Date().getFullYear()}</span>
          <span>Bedrock&nbsp;Titan v2 · Groq&nbsp;Vision · DynamoDB</span>
          <span>Smart Lost &amp; Found</span>
        </div>
      </footer>
    </div>
  );
}
