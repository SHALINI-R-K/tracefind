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
}

export async function createReport(input: {
  type: ReportType;
  description: string;
  category?: string;
  image: string;
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
