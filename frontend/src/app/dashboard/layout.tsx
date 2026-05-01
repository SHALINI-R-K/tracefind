"use client";

import { useState, useEffect } from "react";
import { Authenticator } from "@aws-amplify/ui-react";
import { fetchAuthSession } from "aws-amplify/auth";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Bell,
  ShieldAlert,
  LogOut,
  Search,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  AuthShellHeader,
  AuthShellFooter,
} from "@/shared/components/auth/AuthShellChrome";
import { cn } from "@/shared/lib/utils";
import { listNotifications } from "@/contexts/notification/api/notifications";

type NavItem = {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  adminOnly?: boolean;
};

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/report", label: "Report Item", icon: FileText },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell },
  { href: "/dashboard/admin", label: "Admin", icon: ShieldAlert, adminOnly: true },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Read cognito:groups from the id token to decide whether to show Admin
    const checkAdmin = async () => {
      try {
        const session = await fetchAuthSession();
        const groups = session.tokens?.idToken?.payload?.["cognito:groups"];
        const isMember =
          (Array.isArray(groups) && groups.includes("admin")) ||
          (typeof groups === "string" && groups.split(/[\s,]+/).includes("admin"));
        setIsAdmin(Boolean(isMember));
      } catch {
        setIsAdmin(false);
      }
    };
    checkAdmin();
  }, []);

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

  const visibleNavItems = navItems.filter((item) => !item.adminOnly || isAdmin);

  return (
    <Authenticator
      components={{
        Header: () => <AuthShellHeader />,
        Footer: AuthShellFooter,
      }}
    >
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
            {visibleNavItems.map((item) => {
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

