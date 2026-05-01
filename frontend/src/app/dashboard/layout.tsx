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
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Separator } from "@/shared/components/ui/separator";
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
        setUnreadCount(notifications.filter(n => !n.read).length);
      } catch (e) {
        console.error("Failed to fetch notifications", e);
      }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Authenticator>
      {({ signOut, user }) => (
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="sticky top-0 flex h-screen w-64 flex-col border-r bg-card/50 backdrop-blur-sm">
            {/* Logo */}
            <div className="flex items-center gap-2.5 px-6 py-5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Search className="h-4 w-4" />
              </div>
              <span className="text-lg font-bold tracking-tight">TraceFind</span>
            </div>

            <Separator />

            {/* Nav links */}
            <nav className="flex-1 space-y-1 px-3 py-4">
              {navItems.map((item) => {
                const isActive =
                  item.href === "/dashboard"
                    ? pathname === "/dashboard"
                    : pathname.startsWith(item.href);
                const isNotifications = item.href === "/dashboard/notifications";
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-accent hover:text-foreground"
                    )}
                  >
                    <div className="relative flex items-center gap-3 flex-1">
                      <item.icon className="h-4 w-4" />
                      {item.label}
                      {isNotifications && unreadCount > 0 && (
                        <span className="absolute right-0 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                          {unreadCount > 9 ? "9+" : unreadCount}
                        </span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </nav>

            <Separator />

            {/* User section */}
            <div className="p-4">
              <div className="flex items-center gap-3 rounded-md px-2 py-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary uppercase">
                  {(user?.signInDetails?.loginId ?? "U")[0]}
                </div>
                <div className="flex-1 truncate">
                  <p className="truncate text-sm font-medium">
                    {user?.signInDetails?.loginId ?? "User"}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-2 w-full justify-start text-muted-foreground"
                onClick={signOut}
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </Button>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 overflow-auto">
            <div className="mx-auto max-w-5xl px-8 py-8">{children}</div>
          </main>
        </div>
      )}
    </Authenticator>
  );
}
