"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Plus,
  FileSearch,
  Clock,
  CheckCircle2,
  Inbox,
  Sparkles,
  ArrowUpRight,
} from "lucide-react";
import { ItemReport, listReports } from "@/contexts/reporting/api/reports";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";

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
    {
      label: "Total reports",
      value: items.length,
      icon: FileSearch,
      hint: "All items you've filed",
    },
    {
      label: "Active",
      value: items.filter((i) => i.status === "active").length,
      icon: Clock,
      hint: "Awaiting a match",
    },
    {
      label: "Matched",
      value: items.filter((i) => i.status === "matched" || i.status === "claimed").length,
      icon: CheckCircle2,
      hint: "Reunited or in progress",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Track and manage your lost &amp; found reports.
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/report">
            <Plus className="mr-2 h-4 w-4" strokeWidth={2.25} />
            New report
          </Link>
        </Button>
      </div>

      {/* Stats row */}
      <div className="grid gap-4 sm:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {s.label}
              </CardTitle>
              <s.icon className="h-4 w-4 text-muted-foreground" strokeWidth={1.75} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loading ? <Skeleton className="h-7 w-12" /> : s.value}
              </div>
              <p className="text-xs text-muted-foreground">{s.hint}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {error && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="py-3 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {/* Reports table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <div>
            <CardTitle className="text-base font-semibold">Reports</CardTitle>
            <p className="text-xs text-muted-foreground">
              {loading ? "Loading…" : `${items.length} item${items.length === 1 ? "" : "s"}`}
            </p>
          </div>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          {loading ? (
            <div className="space-y-1 px-6 pb-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 py-2">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}
            </div>
          ) : items.length === 0 ? (
            <EmptyReports />
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="pl-6">Type</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="pr-6 text-right" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((it) => (
                  <TableRow key={it.id} className="cursor-pointer">
                    <TableCell className="pl-6">
                      <Badge variant={it.type as "lost" | "found"}>{it.type}</Badge>
                    </TableCell>
                    <TableCell className="max-w-md truncate font-medium">
                      <Link
                        href={`/dashboard/items/${it.id}`}
                        className="hover:underline"
                      >
                        {it.description}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={it.status as "active" | "matched" | "claimed"}
                        className="text-[0.6rem] px-1.5 py-0"
                      >
                        {it.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(it.created_at).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </TableCell>
                    <TableCell className="pr-6 text-right">
                      <Link
                        href={`/dashboard/items/${it.id}`}
                        className="inline-flex items-center text-xs text-muted-foreground hover:text-foreground"
                      >
                        View
                        <ArrowUpRight className="ml-1 h-3 w-3" strokeWidth={2} />
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function EmptyReports() {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="rounded-full bg-muted p-3">
        <Inbox className="h-6 w-6 text-muted-foreground" strokeWidth={1.5} />
      </div>
      <h3 className="mt-4 text-base font-semibold">No reports yet</h3>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">
        Start by reporting a lost or found item. Matching begins the moment you submit.
      </p>
      <Button className="mt-5" size="sm" asChild>
        <Link href="/dashboard/report">
          <Sparkles className="mr-2 h-4 w-4" strokeWidth={2.25} />
          Create your first report
        </Link>
      </Button>
    </div>
  );
}
