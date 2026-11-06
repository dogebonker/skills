import { it } from "vitest";

it("is fine", () => {
  expect(1).toBe(1);
});

describe("unterminated", () => {
  it("never closes", () => {
    expect(2).toBe(2);
