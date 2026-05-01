"use client";

import { useState, useEffect } from "react";
import { Authenticator } from "@aws-amplify/ui-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Bell,
  ShieldAlert,
  LogOut,
  Search,
  Sparkles,
  ShieldCheck,
  Cpu,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { listNotifications } from "@/contexts/notification/api/notifications";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, ord: "01" },
  { href: "/dashboard/report", label: "Report Item", icon: FileText, ord: "02" },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell, ord: "03" },
  { href: "/dashboard/admin", label: "Admin", icon: ShieldAlert, ord: "04" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const { notifications } = await listNotifications();
        setUnreadCount(notifications.filter((n) => !n.read).length);
      } catch (e) {
        console.error("Failed to fetch notifications", e);
      }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Authenticator components={{ Header: AuthHeader, Footer: AuthFooter }}>
      {({ signOut, user }) => (
        <div className="flex min-h-screen bg-background">
          {/* Sidebar */}
          <aside className="sticky top-0 flex h-screen w-72 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-sm">
            <Link
              href="/"
              className="block px-6 pt-7 pb-5 transition-colors hover:bg-accent/30"
            >
              <div className="flex items-center gap-2.5">
                <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
                  <Search className="h-4 w-4" strokeWidth={2.25} />
                </span>
                <span className="text-lg font-semibold tracking-tight">TraceFind</span>
              </div>
              <p className="mt-2 font-mono text-[0.65rem] uppercase tracking-[0.28em] text-muted-foreground">
                AI-powered recovery
              </p>
            </Link>

            <div className="rule-double mx-6" />

            <nav className="flex-1 overflow-y-auto px-3 pt-5">
              <p className="px-3 pb-2 font-mono text-[0.65rem] uppercase tracking-[0.28em] text-muted-foreground">
                Navigation
              </p>
              <ul className="space-y-0.5">
                {navItems.map((item) => {
                  const isActive =
                    item.href === "/dashboard"
                      ? pathname === "/dashboard"
                      : pathname.startsWith(item.href);
                  const isNotifications = item.href === "/dashboard/notifications";

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={cn(
                          "group relative flex items-center gap-3 rounded-md px-3 py-2.5",
                          "text-sm transition-colors duration-200",
                          isActive
                            ? "bg-primary/10 text-primary ring-1 ring-primary/30"
                            : "text-muted-foreground hover:bg-accent hover:text-foreground"
                        )}
                      >
                        <span
                          className={cn(
                            "font-mono text-[0.65rem] tabular-nums",
                            isActive ? "text-primary/70" : "text-muted-foreground/60"
                          )}
                        >
                          {item.ord}
                        </span>
                        <item.icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
                        <span className="flex-1 font-medium">{item.label}</span>
                        {isNotifications && unreadCount > 0 && (
                          <span
                            className={cn(
                              "flex h-5 min-w-[1.25rem] items-center justify-center rounded-full px-1.5",
                              "font-mono text-[0.65rem] font-bold",
                              isActive
                                ? "bg-primary text-primary-foreground"
                                : "bg-destructive text-destructive-foreground"
                            )}
                          >
                            {unreadCount > 9 ? "9+" : unreadCount}
                          </span>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>

            <div className="border-t border-border p-4">
              <div className="flex items-center gap-3 rounded-md px-2 py-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30 text-xs font-bold uppercase">
                  {(user?.signInDetails?.loginId ?? "U")[0]}
                </div>
                <div className="flex-1 truncate">
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">
                    Signed in
                  </p>
                  <p className="truncate text-[0.8rem] text-foreground">
                    {user?.signInDetails?.loginId ?? "User"}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-2 w-full justify-start text-muted-foreground hover:text-destructive"
                onClick={signOut}
              >
                <LogOut className="mr-2 h-4 w-4" strokeWidth={1.75} />
                Sign out
              </Button>
            </div>
          </aside>

          <main className="relative flex-1 overflow-x-hidden">
            <div
              className="pointer-events-none absolute inset-0 grid-overlay opacity-[0.35]"
              aria-hidden
            />
            <div className="relative mx-auto max-w-5xl px-10 py-12">{children}</div>
          </main>
        </div>
      )}
    </Authenticator>
  );
}

/* ===== Authenticator chrome ============================================
   These render INSIDE the auth card, but we wrap the whole login screen
   with our own background shell via globals.css + body backdrop. The
   Header/Footer here just give the card itself a brand presence.       */

function AuthHeader() {
  return (
    <div className="px-7 pt-7 pb-2">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-3 w-3" strokeWidth={2.25} />
        Back home
      </Link>

      <div className="mt-5 flex items-center gap-2.5">
        <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
          <Search className="h-4 w-4" strokeWidth={2.25} />
        </span>
        <div>
          <p className="text-base font-semibold leading-none tracking-tight">
            TraceFind
          </p>
          <p className="mt-1 font-mono text-[0.6rem] uppercase tracking-[0.25em] text-muted-foreground">
            AI-powered recovery
          </p>
        </div>
      </div>

      <h1 className="mt-6 font-display text-2xl font-bold leading-tight tracking-tight">
        Welcome back.
      </h1>
      <p className="mt-1.5 text-sm text-muted-foreground">
        Sign in to your dashboard or create an account to start matching items.
      </p>
    </div>
  );
}

function AuthFooter() {
  return (
    <div className="border-t border-border bg-card/40 px-7 py-4">
      <div className="flex items-center justify-between font-mono text-[0.6rem] uppercase tracking-[0.22em] text-muted-foreground">
        <span className="inline-flex items-center gap-1.5">
          <ShieldCheck className="h-3 w-3" strokeWidth={2.25} />
          Cognito secured
        </span>
        <span className="inline-flex items-center gap-1.5">
          <Cpu className="h-3 w-3" strokeWidth={2.25} />
          v0.1
        </span>
      </div>
    </div>
  );
}
