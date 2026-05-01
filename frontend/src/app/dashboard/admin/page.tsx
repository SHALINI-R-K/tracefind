"use client";

import { useEffect, useState } from "react";
import { ShieldAlert, Loader2 } from "lucide-react";
import { AdminReport, archiveReport, AuditEntry, listAudit, listReports } from "@/contexts/admin/api/admin";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/shared/components/ui/dialog";
import { Textarea } from "@/shared/components/ui/textarea";
import { Label } from "@/shared/components/ui/label";

export default function AdminPage() {
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [archiveTarget, setArchiveTarget] = useState<string | null>(null);
  const [reason, setReason] = useState("");
  const [reportsCursor, setReportsCursor] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  async function reload() {
    try {
      const [r, a] = await Promise.all([listReports(), listAudit()]);
      setReports(r.reports);
      setReportsCursor(r.next_cursor);
      setAudit(a.entries);
    } catch (e: unknown) { setError((e as Error).message); }
    finally { setLoading(false); }
  }

  async function loadMoreReports() {
    if (!reportsCursor || loadingMore) return;
    setLoadingMore(true);
    try {
      const r = await listReports({ cursor: reportsCursor });
      setReports((prev) => [...prev, ...r.reports]);
      setReportsCursor(r.next_cursor);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setLoadingMore(false);
    }
  }

  useEffect(() => { reload(); }, []);

  async function doArchive() {
    if (!archiveTarget || !reason.trim()) return;
    setBusy(archiveTarget);
    setArchiveTarget(null);
    try { await archiveReport(archiveTarget, reason); await reload(); }
    catch (e: unknown) { setError((e as Error).message); }
    finally { setBusy(null); setReason(""); }
  }

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-6 w-6 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">Admin</h1>
        </div>
        <p className="mt-1 text-muted-foreground">Moderation and audit log. Admin role required.</p>
      </div>

      {error && <Card className="border-destructive/50 bg-destructive/10"><CardContent className="p-4 text-sm text-destructive">{error}</CardContent></Card>}

      <Tabs defaultValue="reports">
        <TabsList>
          <TabsTrigger value="reports">Reports ({reports.length})</TabsTrigger>
          <TabsTrigger value="audit">Audit Log ({audit.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="reports" className="mt-4 space-y-3">
          {loading ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 w-full rounded-lg" />) :
            reports.length === 0 ? <Card><CardContent className="py-8 text-center text-muted-foreground">No reports.</CardContent></Card> :
            reports.map((r) => (
              <Card key={r.id} className="transition-all duration-200 hover:border-primary/30">
                <CardContent className="flex items-center justify-between p-5">
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge variant={r.type as any}>{r.type}</Badge>
                      <span className="font-medium">{r.description}</span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      <Badge variant={r.status as any} className="text-[10px] px-1.5 py-0 mr-1">{r.status}</Badge>
                      {r.id.slice(0, 8)}… · {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {r.status !== "archived" && (
                    <Button variant="destructive" size="sm" disabled={busy === r.id}
                      onClick={() => { setArchiveTarget(r.id); setReason(""); }}>
                      {busy === r.id ? <Loader2 className="h-4 w-4 animate-spin" /> : "Archive"}
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          {!loading && reportsCursor && (
            <div className="flex justify-center pt-2">
              <Button variant="outline" size="sm" onClick={loadMoreReports} disabled={loadingMore}>
                {loadingMore ? <Loader2 className="h-4 w-4 animate-spin" /> : "Load more"}
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="audit" className="mt-4">
          <Card>
            <CardHeader><CardTitle className="text-lg">Audit Log</CardTitle></CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-40 w-full" /> :
                audit.length === 0 ? <p className="text-muted-foreground text-center py-8">No audit entries.</p> : (
                <div className="overflow-auto">
                  <table className="w-full text-sm">
                    <thead><tr className="border-b text-left text-muted-foreground">
                      <th className="pb-3 font-medium">Action</th>
                      <th className="pb-3 font-medium">Actor</th>
                      <th className="pb-3 font-medium">Target</th>
                      <th className="pb-3 font-medium">Date</th>
                    </tr></thead>
                    <tbody>{audit.map((e) => (
                      <tr key={e.id} className="border-b last:border-0">
                        <td className="py-3 font-medium">{e.action}</td>
                        <td className="py-3 text-muted-foreground">{e.actor_user_id.slice(0, 8)}…</td>
                        <td className="py-3 text-muted-foreground">{e.target_id.slice(0, 8)}…</td>
                        <td className="py-3 text-muted-foreground">{new Date(e.created_at).toLocaleString()}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Archive Dialog */}
      <Dialog open={!!archiveTarget} onOpenChange={() => setArchiveTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive this report?</DialogTitle>
            <DialogDescription>Provide a reason for archiving. This action will be logged in the audit trail.</DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="reason">Reason</Label>
            <Textarea id="reason" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Duplicate report" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setArchiveTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={doArchive} disabled={!reason.trim()}>Archive</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
