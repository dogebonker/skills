import { describe, expect, it, vi } from "vitest";

// tree-sitter-typescript reports an ERROR for `typeof import(...)` in type arguments (seen in t3code).
vi.mock("node:fs", async (importOriginal) => ({
  ...(await importOriginal<typeof import("node:fs")>()),
  existsSync: () => true,
}));

describe("mocked fs", () => {
  it("sees the mock", () => {
    expect(true).toBe(true);
  });

  it("is dropped", () => {
    const real = String.raw`C:\Users\a b\x`;
    expect(real).toContain("Users");
  });
});
