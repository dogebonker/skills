export {};

// Strategy: a function type is the strategy interface; pass the algorithm as a value.
type ShippingStrategy = (weightKg: number) => number;

const flatRate: ShippingStrategy = () => 5;
const perKilo = (rate: number): ShippingStrategy => (kg) => kg * rate;
const freeOverTen: ShippingStrategy = (kg) => (kg > 10 ? 0 : 7.5);

const strategies = { flatRate, perKilo: perKilo(1.2), freeOverTen } satisfies Record<string, ShippingStrategy>;

class Cart {
  readonly #weightKg: number;
  #shipping: ShippingStrategy;

  constructor(weightKg: number, shipping: ShippingStrategy) {
    this.#weightKg = weightKg;
    this.#shipping = shipping;
  }

  setShipping(s: ShippingStrategy): void {
    this.#shipping = s;
  }

  shippingCost(): number {
    return this.#shipping(this.#weightKg);
  }
}

const cart = new Cart(12, flatRate);
for (const [name, strategy] of Object.entries(strategies)) {
  cart.setShipping(strategy);
  console.log(name, cart.shippingCost().toFixed(2));
}
