import { fetchAuthSession } from "aws-amplify/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken?.toString();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const code = body?.error?.code ?? res.status;
    const msg = body?.error?.message ?? res.statusText;
    throw new ApiError(`${code}: ${msg}`, res.status, code);
  }
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(message: string, public status: number, public code: string) {
    super(message);
  }
}
