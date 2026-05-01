"use client";

import { useEffect, useState } from "react";
import { Bell, Check, BellOff } from "lucide-react";
import {
  listNotifications,
  markRead,
  Notification,
} from "@/contexts/notification/api/notifications";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    try {
      const r = await listNotifications();
      setItems(r.notifications);
      setError(null);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reload();
    const t = setInterval(reload, 10_000);
    return () => clearInterval(t);
  }, []);

  const unreadCount = items.filter((n) => !n.read).length;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Notifications</h1>
          <p className="text-sm text-muted-foreground">
            {unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}
          </p>
        </div>
        {unreadCount > 0 && (
          <Badge variant="default">{unreadCount} new</Badge>
        )}
      </div>

      {error && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="py-3 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {/* Body */}
      {loading ? (
        <Card>
          <CardContent className="space-y-3 py-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-md" />
            ))}
          </CardContent>
        </Card>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-muted p-3">
              <BellOff className="h-6 w-6 text-muted-foreground" strokeWidth={1.5} />
            </div>
            <h3 className="mt-4 text-base font-semibold">No notifications yet</h3>
            <p className="mt-1 max-w-sm text-sm text-muted-foreground">
              You&apos;ll be notified here the moment a likely match for one of your
              items appears.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((n) => (
            <Card
              key={n.id}
              className={cn(
                "transition-colors",
                !n.read && "border-primary/30 bg-primary/[0.04]"
              )}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex flex-1 items-start gap-3">
                    <div
                      className={cn(
                        "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md",
                        !n.read
                          ? "bg-primary/15 text-primary ring-1 ring-primary/30"
                          : "bg-muted text-muted-foreground"
                      )}
                    >
                      <Bell className="h-4 w-4" strokeWidth={1.75} />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium capitalize">
                          {n.type.replace(/_/g, " ")}
                        </p>
                        {!n.read && (
                          <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-label="unread" />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(n.created_at).toLocaleString()}
                      </p>

                      {n.type === "match_found" && n.payload && (
                        <div className="mt-3 rounded-md border border-border bg-muted/30 p-3">
                          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                            Match details
                          </p>
                          <dl className="space-y-1.5 text-sm">
                            <div className="flex items-start gap-2">
                              <dt className="w-24 shrink-0 text-xs text-muted-foreground">Email</dt>
                              <dd className="text-foreground">
                                {(n.payload?.other_party_email as string) ?? "N/A"}
                              </dd>
                            </div>
                            <div className="flex items-start gap-2">
                              <dt className="w-24 shrink-0 text-xs text-muted-foreground">Item</dt>
                              <dd className="text-foreground">
                                {(n.payload?.other_item_description as string) ?? "No description"}
                              </dd>
                            </div>
                            <div className="flex items-start gap-2">
                              <dt className="w-24 shrink-0 text-xs text-muted-foreground">Score</dt>
                              <dd>
                                <Badge variant="secondary" className="h-5 text-[0.65rem]">
                                  {n.payload?.score
                                    ? ((n.payload.score as number) * 100).toFixed(1)
                                    : "0.0"}
                                  % match
                                </Badge>
                              </dd>
                            </div>
                          </dl>
                        </div>
                      )}

                      {n.type !== "match_found" &&
                        n.payload &&
                        Object.keys(n.payload).length > 0 && (
                          <pre className="mt-2 overflow-auto rounded-md border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
                            {JSON.stringify(n.payload, null, 2)}
                          </pre>
                        )}
                    </div>
                  </div>
                  {!n.read && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        markRead(n.id).then(reload);
                      }}
                    >
                      <Check className="mr-1.5 h-3.5 w-3.5" strokeWidth={2} />
                      Mark read
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
