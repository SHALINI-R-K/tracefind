"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  Plus,
  FileSearch,
  Clock,
  CheckCircle2,
  Inbox,
  Sparkles,
} from "lucide-react";
import { ItemReport, listReports } from "@/contexts/reporting/api/reports";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";

export default function DashboardPage() {
  const [items, setItems] = useState<ItemReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listReports()
      .then((r) => {
        setItems(r.items);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const stats = [
    { label: "Total reports", value: items.length, icon: FileSearch, accent: "text-primary" },
    {
      label: "Active",
      value: items.filter((i) => i.status === "active").length,
      icon: Clock,
      accent: "text-status-matched",
    },
    {
      label: "Matched",
      value: items.filter((i) => i.status === "matched" || i.status === "claimed").length,
      icon: CheckCircle2,
      accent: "text-status-found",
    },
  ];

  return (
    <div className="space-y-12">
      {/* Header */}
      <header className="opacity-0 animate-fade-in-up">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted-foreground">
          Section&nbsp;01 &mdash; Dashboard
        </p>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-6">
          <h1 className="font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl">
            Your <span className="underline-accent">reports</span>.
          </h1>
          <Button asChild size="lg">
            <Link href="/dashboard/report">
              <Plus className="mr-2 h-4 w-4" strokeWidth={2.25} />
              New report
            </Link>
          </Button>
        </div>
      </header>

      <div className="rule-double opacity-0 animate-fade-in-up [animation-delay:120ms]" />

      {/* Stats — running figures */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3 opacity-0 animate-fade-in-up [animation-delay:200ms]">
        {stats.map((s) => (
          <div
            key={s.label}
            className="
              relative overflow-hidden rounded-md border border-border bg-card/40 px-5 py-5
              transition-[border-color,background] duration-300 ease-ink
              hover:border-primary/40 hover:bg-card
            "
          >
            <div className="flex items-start justify-between">
              <p className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
                {s.label}
              </p>
              <s.icon className={`h-4 w-4 ${s.accent}`} strokeWidth={1.75} />
            </div>
            <p className={`index-number mt-3 text-5xl ${s.accent}`}>
              {loading ? <span className="text-muted-foreground/30">·</span> : s.value}
            </p>
          </div>
        ))}
      </section>

      <div className="rule-double opacity-0 animate-fade-in-up [animation-delay:260ms]" />

      {/* Error */}
      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-5 py-4 text-sm text-destructive">
          <span className="font-mono text-xs uppercase tracking-[0.18em]">Error · </span>
          {error}
        </div>
      )}

      {/* Reports grid */}
      <section className="opacity-0 animate-fade-in-up [animation-delay:320ms]">
        <div className="mb-6 flex items-baseline justify-between">
          <h2 className="font-display text-2xl font-bold tracking-tight">My reports</h2>
          <p className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
            {loading ? "loading…" : `${items.length} on the board`}
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="board-card p-5">
                <Skeleton className="h-32 w-full rounded-sm" />
                <Skeleton className="mt-4 h-4 w-1/3" />
                <Skeleton className="mt-2 h-5 w-3/4" />
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <EmptyBoard />
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((it, i) => (
              <ReportCard key={it.id} item={it} index={i} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

/* ---------- Subcomponents ----------------------------------------------- */

function ReportCard({ item, index }: { item: ItemReport; index: number }) {
  return (
    <Link
      href={`/dashboard/items/${item.id}`}
      className="group board-card block p-5 opacity-0 animate-fade-in-up"
      style={{ animationDelay: `${340 + index * 60}ms` }}
    >
      {/* Header strip */}
      <div className="mb-4 flex items-start justify-between">
        <Badge variant={item.type as "lost" | "found"}>{item.type}</Badge>
        <span className="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-muted-foreground">
          №&nbsp;{String(index + 1).padStart(3, "0")}
        </span>
      </div>

      {/* Description headline */}
      <h3 className="text-base font-semibold leading-snug tracking-tight text-foreground">
        {item.description.length > 70
          ? item.description.slice(0, 70) + "…"
          : item.description}
      </h3>

      {/* Metadata */}
      <dl className="mt-5 space-y-1.5 font-mono text-[0.7rem] uppercase tracking-[0.16em] text-muted-foreground">
        <div className="flex items-center gap-3">
          <dt className="w-14 shrink-0">Status</dt>
          <dd>
            <Badge
              variant={item.status as "active" | "matched" | "claimed"}
              className="text-[0.6rem] px-1.5 py-0"
            >
              {item.status}
            </Badge>
          </dd>
        </div>
        <div className="flex items-center gap-3">
          <dt className="w-14 shrink-0">Filed</dt>
          <dd className="normal-case tracking-normal text-foreground/70">
            {new Date(item.created_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
            })}
          </dd>
        </div>
      </dl>

      {/* Footer affordance */}
      <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
        <span className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
          View report
        </span>
        <ArrowUpRight
          className="h-4 w-4 text-muted-foreground transition-transform duration-300 ease-ink group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-primary"
          strokeWidth={1.75}
        />
      </div>
    </Link>
  );
}

function EmptyBoard() {
  return (
    <div className="relative overflow-hidden rounded-md border border-dashed border-border bg-card/30 px-8 py-20 text-center">
      <div
        className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent"
        aria-hidden
      />
      <Inbox className="mx-auto h-10 w-10 text-muted-foreground" strokeWidth={1.25} />
      <p className="mt-5 font-display text-2xl font-semibold leading-tight tracking-tight">
        No reports yet.
      </p>
      <p className="mx-auto mt-3 max-w-md text-muted-foreground">
        Start by reporting a lost or found item. Matching begins the moment you submit.
      </p>
      <Button className="mt-7" asChild>
        <Link href="/dashboard/report">
          <Sparkles className="mr-2 h-4 w-4" strokeWidth={2.25} />
          Create your first report
        </Link>
      </Button>
    </div>
  );
}
