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
  ShieldCheck,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { listNotifications } from "@/contexts/notification/api/notifications";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/report", label: "Report Item", icon: FileText },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell },
  { href: "/dashboard/admin", label: "Admin", icon: ShieldAlert },
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
      <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-sm">
        <Link
          href="/"
          className="flex items-center gap-2.5 px-5 py-4 transition-colors hover:bg-accent/30"
        >
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
            <Search className="h-3.5 w-3.5" strokeWidth={2.25} />
          </span>
          <span className="text-base font-semibold tracking-tight">TraceFind</span>
        </Link>

        <div className="border-t border-border" />

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
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
                      "group flex items-center gap-2.5 rounded-md px-3 py-2 text-sm",
                      "transition-colors duration-150",
                      isActive
                        ? "bg-accent text-foreground"
                        : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
                    <span className="flex-1 font-medium">{item.label}</span>
                    {isNotifications && unreadCount > 0 && (
                      <span
                        className={cn(
                          "flex h-5 min-w-[1.25rem] items-center justify-center rounded-full px-1.5 text-xs font-semibold",
                          "bg-primary text-primary-foreground"
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

        <div className="border-t border-border p-3">
          <div className="flex items-center gap-2.5 rounded-md px-2 py-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15 text-primary text-xs font-semibold uppercase ring-1 ring-primary/30">
              {(user?.signInDetails?.loginId ?? "U")[0]}
            </div>
            <div className="flex-1 truncate">
              <p className="truncate text-sm font-medium text-foreground">
                {user?.signInDetails?.loginId ?? "User"}
              </p>
              <p className="truncate text-xs text-muted-foreground">Signed in</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="mt-1 w-full justify-start text-muted-foreground hover:text-destructive"
            onClick={signOut}
          >
            <LogOut className="mr-2 h-4 w-4" strokeWidth={1.75} />
            Sign out
          </Button>
        </div>
      </aside>

      {/* Main */}
      <main className="relative flex-1 overflow-x-hidden">
        <div className="mx-auto max-w-6xl px-8 py-8">{children}</div>
      </main>
    </div>
      )}
    </Authenticator>
  );
}

/* ===== Authenticator chrome ============================================ */

function AuthHeader() {
  return (
    <div className="px-7 pt-7 pb-2">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-3 w-3" strokeWidth={2.25} />
        Back home
      </Link>

      <div className="mt-5 flex items-center gap-2.5">
        <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
          <Search className="h-4 w-4" strokeWidth={2.25} />
        </span>
        <p className="text-base font-semibold leading-none tracking-tight">TraceFind</p>
      </div>

      <h1 className="mt-6 text-2xl font-bold leading-tight tracking-tight">
        Welcome back
      </h1>
      <p className="mt-1.5 text-sm text-muted-foreground">
        Sign in to your dashboard or create an account.
      </p>
    </div>
  );
}

function AuthFooter() {
  return (
    <div className="border-t border-border bg-card/40 px-7 py-3">
      <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <ShieldCheck className="h-3 w-3" strokeWidth={2.25} />
        Secured by Cognito
      </p>
    </div>
  );
}
