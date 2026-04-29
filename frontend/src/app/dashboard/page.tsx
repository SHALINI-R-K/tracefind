"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, ArrowRight, FileSearch, Clock, CheckCircle2 } from "lucide-react";
import { ItemReport, listReports } from "@/contexts/reporting/api/reports";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
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

  const stats = {
    total: items.length,
    active: items.filter((i) => i.status === "active").length,
    matched: items.filter((i) => i.status === "matched" || i.status === "claimed").length,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-muted-foreground">
            Manage your lost and found reports
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/report">
            <Plus className="mr-2 h-4 w-4" />
            New report
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: "Total Reports", value: stats.total, icon: FileSearch, color: "text-primary" },
          { label: "Active", value: stats.active, icon: Clock, color: "text-amber-400" },
          { label: "Matched", value: stats.matched, icon: CheckCircle2, color: "text-emerald-400" },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="flex items-center gap-4 p-6">
              <div className={`rounded-lg bg-muted p-2.5 ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold">
                  {loading ? "—" : stat.value}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Error */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/10">
          <CardContent className="p-4 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">My Reports</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 rounded-lg border p-4">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))
          ) : items.length === 0 ? (
            <div className="py-12 text-center">
              <FileSearch className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p className="mt-4 text-muted-foreground">
                No reports yet. Start by reporting a lost or found item.
              </p>
              <Button className="mt-4" asChild>
                <Link href="/dashboard/report">
                  <Plus className="mr-2 h-4 w-4" />
                  Create your first report
                </Link>
              </Button>
            </div>
          ) : (
            items.map((it, i) => (
              <Link
                key={it.id}
                href={`/dashboard/items/${it.id}`}
                className="group flex items-center justify-between rounded-lg border p-4 transition-all duration-200 hover:border-primary/30 hover:bg-accent/50"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <FileSearch className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge variant={it.type as "lost" | "found"}>{it.type}</Badge>
                      <span className="font-medium">{it.description}</span>
                    </div>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant={it.status as any} className="text-[10px] px-1.5 py-0">
                        {it.status}
                      </Badge>
                      <span>·</span>
                      <span>{new Date(it.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-primary" />
              </Link>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
