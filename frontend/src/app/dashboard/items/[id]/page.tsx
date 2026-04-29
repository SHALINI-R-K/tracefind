"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, CheckCircle2, XCircle, Search } from "lucide-react";
import { getReport, ItemReport } from "@/contexts/reporting/api/reports";
import { listMatches, Match } from "@/contexts/matching/api/matches";
import { decideClaim } from "@/contexts/claims/api/claims";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { Skeleton } from "@/shared/components/ui/skeleton";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/shared/components/ui/dialog";

export default function ItemDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [item, setItem] = useState<ItemReport | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [confirmDialog, setConfirmDialog] = useState<{ matchId: string; decision: "confirm" | "reject" } | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [it, m] = await Promise.all([getReport(id), listMatches(id)]);
        if (!cancelled) {
          setItem(it);
          setMatches(m.matches);
        }
      } catch (e: unknown) {
        if (!cancelled) setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => { cancelled = true; clearInterval(t); };
  }, [id]);

  async function onDecide() {
    if (!confirmDialog) return;
    setBusy(confirmDialog.matchId);
    setConfirmDialog(null);
    try {
      await decideClaim({ itemId: id, matchId: confirmDialog.matchId, decision: confirmDialog.decision });
      const m = await listMatches(id);
      setMatches(m.matches);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-48" />
        <div className="grid gap-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/10">
        <CardContent className="p-6 text-destructive">{error}</CardContent>
      </Card>
    );
  }
  if (!item) return null;

  return (
    <div className="space-y-8">
      {/* Back */}
      <Button variant="ghost" size="sm" asChild>
        <Link href="/dashboard">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to dashboard
        </Link>
      </Button>

      {/* Item Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Badge variant={item.type as "lost" | "found"} className="text-sm">
              {item.type}
            </Badge>
            <Badge variant={item.status as any}>{item.status}</Badge>
          </div>
          <CardTitle className="mt-2">{item.description}</CardTitle>
          <CardDescription>
            {item.category ?? "Uncategorized"} · Created{" "}
            {new Date(item.created_at).toLocaleString()}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Matches */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Potential Matches</h2>
        {matches.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Search className="mx-auto h-12 w-12 text-muted-foreground/50 animate-pulse" />
              <p className="mt-4 text-muted-foreground">
                {item.status === "active"
                  ? "Searching for matches… we'll notify you when something turns up."
                  : "No matches found."}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {matches.map((m) => {
              const pct = Math.round(m.score * 100);
              return (
                <Card key={m.id} className="transition-all duration-200 hover:border-primary/30">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="space-y-3 flex-1">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl font-bold text-primary">
                            {pct}%
                          </span>
                          <span className="text-sm text-muted-foreground">
                            similarity
                          </span>
                          <Badge variant={m.status as any}>{m.status}</Badge>
                        </div>
                        <Progress value={pct} className="h-2" />
                        <p className="text-xs text-muted-foreground">
                          Lost: {m.lost_item_id.slice(0, 8)}… · Found:{" "}
                          {m.found_item_id.slice(0, 8)}…
                        </p>
                      </div>

                      {m.status === "pending" && item.status === "active" && (
                        <div className="flex gap-2 ml-4">
                          <Button
                            size="sm"
                            disabled={busy === m.id}
                            onClick={() => setConfirmDialog({ matchId: m.id, decision: "confirm" })}
                          >
                            {busy === m.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <>
                                <CheckCircle2 className="mr-1.5 h-4 w-4" />
                                Confirm
                              </>
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={busy === m.id}
                            onClick={() => setConfirmDialog({ matchId: m.id, decision: "reject" })}
                          >
                            <XCircle className="mr-1.5 h-4 w-4" />
                            Reject
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Confirm Dialog */}
      <Dialog open={!!confirmDialog} onOpenChange={() => setConfirmDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {confirmDialog?.decision === "confirm" ? "Confirm this match?" : "Reject this match?"}
            </DialogTitle>
            <DialogDescription>
              {confirmDialog?.decision === "confirm"
                ? "This will mark both items as claimed and notify the other party."
                : "This match will be dismissed and won't appear again."}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDialog(null)}>
              Cancel
            </Button>
            <Button
              variant={confirmDialog?.decision === "confirm" ? "default" : "destructive"}
              onClick={onDecide}
            >
              {confirmDialog?.decision === "confirm" ? "Confirm claim" : "Reject match"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
