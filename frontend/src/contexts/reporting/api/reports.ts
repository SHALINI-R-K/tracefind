import { apiFetch } from "@/shared/lib/api";

export type ReportType = "lost" | "found";

export interface ItemReport {
  id: string;
  user_id: string;
  type: ReportType;
  description: string;
  category: string | null;
  status: "active" | "matched" | "claimed" | "archived";
  created_at: string;
  location?: string | null;
  incident_at?: string | null;
  photo_count?: number;
}

export async function createReport(input: {
  type: ReportType;
  description: string;
  category?: string;
  /** 1..3 image data URIs (JPEG/PNG/WebP, ≤5 MB each, already client-side-resized). */
  images: string[];
  /** Free-text location, e.g. "A-block 210 cafeteria". */
  location?: string;
  /** ISO 8601 timestamp of when the loss/finding actually happened. */
  incident_at?: string;
}): Promise<ItemReport> {
  return apiFetch<ItemReport>("/items", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function listReports(): Promise<{ items: ItemReport[] }> {
  return apiFetch<{ items: ItemReport[] }>("/items");
}

export async function getReport(id: string): Promise<ItemReport> {
  return apiFetch<ItemReport>(`/items/${id}`);
}
