import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiFetch, ApiError } from "./api";

vi.mock("aws-amplify/auth", () => ({
  fetchAuthSession: vi.fn(async () => ({
    tokens: { idToken: { toString: () => "test-token" } },
  })),
}));

const fetchMock = vi.fn();
beforeEach(() => {
  fetchMock.mockReset();
  globalThis.fetch = fetchMock;
});

describe("apiFetch", () => {
  it("attaches Authorization header from Cognito session", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    });
    await apiFetch("/items");
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBe(
      "Bearer test-token"
    );
  });

  it("throws ApiError with code and status on non-2xx", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: async () => ({ error: { code: "CONFLICT", message: "already claimed" } }),
    });
    await expect(apiFetch("/items/x/claim", { method: "POST" })).rejects.toMatchObject({
      status: 409,
      code: "CONFLICT",
    });
    const err = await apiFetch("/items/x/claim", { method: "POST" }).catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
  });
});
