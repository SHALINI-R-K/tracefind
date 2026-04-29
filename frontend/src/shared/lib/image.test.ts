import { describe, it, expect, vi } from "vitest";
import { fileToResizedDataUri } from "./image";

describe("fileToResizedDataUri", () => {
  it("returns a JPEG data URI within bounds", async () => {
    // @ts-expect-error stub createImageBitmap
    globalThis.createImageBitmap = vi.fn(async () => ({
      width: 4000,
      height: 2000,
    }));

    const ctx = { drawImage: vi.fn() };
    HTMLCanvasElement.prototype.getContext = vi.fn(() => ctx) as never;
    HTMLCanvasElement.prototype.toDataURL = vi.fn(
      () => "data:image/jpeg;base64,abc"
    );

    const file = new File([new Uint8Array(8)], "f.jpg", { type: "image/jpeg" });
    const uri = await fileToResizedDataUri(file, 1024);
    expect(uri.startsWith("data:image/jpeg;base64,")).toBe(true);
  });
});
