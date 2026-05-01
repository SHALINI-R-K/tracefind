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

export async function listReports(
  opts: { status?: string; cursor?: string; limit?: number } = {}
): Promise<{ reports: AdminReport[]; next_cursor: string | null }> {
  const params = new URLSearchParams();
  if (opts.status) params.set("status", opts.status);
  if (opts.cursor) params.set("cursor", opts.cursor);
  if (opts.limit) params.set("limit", String(opts.limit));
  const qs = params.toString();
  return apiFetch(`/admin/reports${qs ? `?${qs}` : ""}`);
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
