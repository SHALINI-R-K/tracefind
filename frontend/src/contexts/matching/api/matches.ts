import { apiFetch } from "@/shared/lib/api";

export interface Match {
  id: string;
  lost_item_id: string;
  found_item_id: string;
  score: number;
  status: "pending" | "confirmed" | "rejected";
  created_at: string;
}

export async function listMatches(itemId: string): Promise<{ matches: Match[] }> {
  return apiFetch<{ matches: Match[] }>(`/items/${itemId}/matches`);
}
