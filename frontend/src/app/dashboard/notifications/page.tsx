"use client";

import { useEffect, useState } from "react";
import { Bell, Check, BellOff } from "lucide-react";
import { listNotifications, markRead, Notification } from "@/contexts/notification/api/notifications";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    try { const r = await listNotifications(); setItems(r.notifications); }
    catch (e: unknown) { setError((e as Error).message); }
    finally { setLoading(false); }
  }

  useEffect(() => { reload(); const t = setInterval(reload, 10_000); return () => clearInterval(t); }, []);

  const unreadCount = items.filter((n) => !n.read).length;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="mt-1 text-muted-foreground">{unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}</p>
        </div>
        {unreadCount > 0 && <Badge className="text-sm px-3 py-1">{unreadCount} new</Badge>}
      </div>

      {error && <Card className="border-destructive/50 bg-destructive/10"><CardContent className="p-4 text-sm text-destructive">{error}</CardContent></Card>}

      {loading ? (
        <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-lg" />)}</div>
      ) : items.length === 0 ? (
        <Card><CardContent className="py-12 text-center"><BellOff className="mx-auto h-12 w-12 text-muted-foreground/50" /><p className="mt-4 text-muted-foreground">No notifications yet.</p></CardContent></Card>
      ) : (
        <div className="space-y-3">
          {items.map((n) => (
            <Card key={n.id} className={cn("transition-all duration-200 hover:border-primary/30", !n.read && "border-primary/20 bg-primary/5")}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={cn("mt-0.5 rounded-lg p-2", !n.read ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground")}><Bell className="h-4 w-4" /></div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium capitalize">{n.type.replace(/_/g, " ")}</p>
                        {!n.read && <span className="h-2 w-2 rounded-full bg-primary" />}
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">{new Date(n.created_at).toLocaleString()}</p>
                      
                      {n.type === "match_found" && n.payload && (
                        <div className="mt-4 rounded-md border bg-muted/30 p-4">
                          <h4 className="text-sm font-semibold mb-2">Match Details</h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex items-start gap-2">
                              <span className="font-medium text-muted-foreground w-20">Email:</span>
                              <span className="text-foreground">{(n.payload?.other_party_email as string) ?? "N/A"}</span>
                            </div>
                            <div className="flex items-start gap-2">
                              <span className="font-medium text-muted-foreground w-20">Description:</span>
                              <span className="text-foreground italic">"{(n.payload?.other_item_description as string) ?? "No description"}"</span>
                            </div>
                            <div className="flex items-start gap-2">
                              <span className="font-medium text-muted-foreground w-20">Score:</span>
                              <Badge variant="secondary" className="h-5 text-[10px]">
                                {n.payload?.score ? ((n.payload.score as number) * 100).toFixed(1) : "0.0"}% match
                              </Badge>
                            </div>
                          </div>
                        </div>
                      )}

                      {n.type !== "match_found" && n.payload && Object.keys(n.payload).length > 0 && (
                        <pre className="mt-3 overflow-auto rounded-md bg-muted/50 p-3 text-xs text-muted-foreground">{JSON.stringify(n.payload, null, 2)}</pre>
                      )}
                    </div>
                  </div>
                  {!n.read && <Button variant="ghost" size="sm" onClick={() => { markRead(n.id).then(reload); }}><Check className="mr-1.5 h-3.5 w-3.5" />Read</Button>}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
