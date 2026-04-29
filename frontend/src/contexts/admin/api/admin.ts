import { apiFetch } from "@/shared/lib/api";

export interface AdminReport {
  id: string;
  user_id: string;
  type: "lost" | "found";
  description: string;
  category: string | null;
  status: string;
  created_at: string;
}

export interface AuditEntry {
  id: string;
  actor_user_id: string;
  action: string;
  target_id: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  created_at: string;
}

export async function listReports(status?: string): Promise<{ reports: AdminReport[] }> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch(`/admin/reports${qs}`);
}

export async function archiveReport(id: string, reason: string): Promise<unknown> {
  return apiFetch(`/admin/items/${id}/archive`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export async function listAudit(): Promise<{
  entries: AuditEntry[];
  next_cursor: string | null;
}> {
  return apiFetch(`/admin/audit`);
}
