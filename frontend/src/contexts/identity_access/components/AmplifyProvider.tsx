"use client";

import { Amplify } from "aws-amplify";
import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { ReactNode, useMemo } from "react";

export function AmplifyProvider({ children }: { children: ReactNode }) {
  useMemo(() => {
    Amplify.configure({
      Auth: {
        Cognito: {
          userPoolId: process.env.NEXT_PUBLIC_USER_POOL_ID ?? "",
          userPoolClientId: process.env.NEXT_PUBLIC_USER_POOL_CLIENT_ID ?? "",
        },
      },
    });
  }, []);

  return <Authenticator.Provider>{children}</Authenticator.Provider>;
}
