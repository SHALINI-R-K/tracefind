"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Authenticator } from "@aws-amplify/ui-react";
import {
  AuthShellHeader,
  AuthShellFooter,
} from "@/shared/components/auth/AuthShellChrome";

export default function SignInPage() {
  return (
    <Authenticator
      initialState="signIn"
      components={{
        Header: () => (
          <AuthShellHeader
            title="Welcome back"
            subtitle="Sign in to pick up where you left off."
          />
        ),
        Footer: AuthShellFooter,
      }}
    >
      {() => <RedirectToDashboard />}
    </Authenticator>
  );
}

/**
 * The Authenticator only renders its children once the user is
 * authenticated, so any markup here means we should bounce them on to
 * the dashboard. We render a tiny "Redirecting…" stub for the brief
 * moment between auth-success and the route change.
 */
function RedirectToDashboard() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/dashboard");
  }, [router]);
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-sm text-muted-foreground">Redirecting to your dashboard…</p>
    </div>
  );
}
