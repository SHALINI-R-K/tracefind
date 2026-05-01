"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Authenticator } from "@aws-amplify/ui-react";
import {
  AuthShellHeader,
  AuthShellFooter,
} from "@/shared/components/auth/AuthShellChrome";

export default function SignUpPage() {
  return (
    <Authenticator
      initialState="signUp"
      components={{
        Header: () => (
          <AuthShellHeader
            title="Create your account"
            subtitle="A 30-second setup. Then start pinning lost or found items."
          />
        ),
        Footer: AuthShellFooter,
      }}
    >
      {() => <RedirectToDashboard />}
    </Authenticator>
  );
}

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
