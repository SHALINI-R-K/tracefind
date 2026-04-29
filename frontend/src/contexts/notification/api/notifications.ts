import { apiFetch } from "@/shared/lib/api";

export interface Notification {
  id: string;
  type: "match_found" | "claim_confirmed" | "claim_rejected";
  payload: Record<string, unknown>;
  read: boolean;
  created_at: string;
}

export async function listNotifications(): Promise<{
  notifications: Notification[];
  next_cursor: string | null;
}> {
  return apiFetch("/notifications");
}

export async function markRead(id: string): Promise<void> {
  await apiFetch(`/notifications/${id}/read`, { method: "POST" });
}
