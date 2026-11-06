import { beforeEach, describe, expect, it, test } from "vitest";
import { Cart } from "./cart";

describe("Cart", () => {
  let cart: Cart;

  beforeEach(() => {
    cart = new Cart();
  });

  it("starts empty", () => {
    expect(cart.items).toEqual([]);
  });

  describe("add", () => {
    it("adds an item", () => {
      cart.add("apple");
      expect(cart.items).toHaveLength(1);
    });

    it("adds an item", () => {
      cart.add("pear");
      expect(cart.items).toEqual(["pear"]);
    }); // duplicate title on purpose

    it.each([1, 2, 3])("adds %i units", (n) => {
      cart.add("apple", n);
      expect(cart.count("apple")).toBe(n);
    });
  });

  describe.each([["EUR"], ["USD"]])("totals in %s", (currency) => {
    test(`formats ${currency}`, () => {
      expect(cart.total(currency)).toMatch(/0/);
    });
  });

  it.skip("applies a coupon", () => {});
  it.todo("supports gift cards");

  test.each`
    a    | b    | sum
    ${1} | ${1} | ${2}
  `("adds $a + $b", ({ a, b, sum }) => {
    expect(a + b).toBe(sum);
  });

  it("préfère les accents 日本語", () => {
    expect("é".length).toBe(1);
  });

  if (process.env.SLOW) it("only when slow", () => {});
});

describe("Empty after delete", () => {
  it("is the only test here", () => {
    expect(true).toBe(true);
  });
});
