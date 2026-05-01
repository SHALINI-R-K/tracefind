"use client";

import Link from "next/link";
import { ArrowLeft, Search, ShieldCheck } from "lucide-react";

export interface AuthShellHeaderProps {
  title?: string;
  subtitle?: string;
}

/**
 * Branded card header used inside the Cognito Authenticator on
 * /signin, /signup, and the /dashboard fallback. The Authenticator
 * passes this in via its `components.Header` slot.
 */
export function AuthShellHeader({
  title = "Welcome back",
  subtitle = "Sign in to your dashboard or create an account.",
}: AuthShellHeaderProps) {
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
        <p className="text-base font-semibold leading-none tracking-tight">
          TraceFind
        </p>
      </div>

      <h1 className="mt-6 text-2xl font-bold leading-tight tracking-tight">
        {title}
      </h1>
      <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
    </div>
  );
}

export function AuthShellFooter() {
  return (
    <div className="border-t border-border bg-card/40 px-7 py-3">
      <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <ShieldCheck className="h-3 w-3" strokeWidth={2.25} />
        Secured by Cognito
      </p>
    </div>
  );
}
