import { apiFetch } from "@/shared/lib/api";

export interface Claim {
  id: string;
  match_id: string;
  status: "pending" | "confirmed" | "rejected";
  created_at: string;
  resolved_at: string | null;
}

export async function decideClaim(input: {
  itemId: string;
  matchId: string;
  decision: "confirm" | "reject";
}): Promise<Claim> {
  return apiFetch<Claim>(`/items/${input.itemId}/claim`, {
    method: "POST",
    body: JSON.stringify({
      match_id: input.matchId,
      decision: input.decision,
    }),
  });
}
