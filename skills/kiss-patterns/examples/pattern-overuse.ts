export {};

// Pattern overuse: an interface with one implementation, a factory with one product
// and a singleton wrapping a pure calculation. The fix is a function.

// --- Violation ---
interface IPriceCalculator {
  priceWithTax(netCents: number): number;
}
class DefaultPriceCalculator implements IPriceCalculator {
  priceWithTax(netCents: number): number {
    return Math.round(netCents * 1.23);
  }
}
class PriceCalculatorFactory {
  static create(): IPriceCalculator {
    return new DefaultPriceCalculator();
  }
}
class PricingService {
  static #instance: PricingService | undefined;
  readonly #calculator: IPriceCalculator;
  private constructor() {
    this.#calculator = PriceCalculatorFactory.create();
  }
  static getInstance(): PricingService {
    PricingService.#instance ??= new PricingService();
    return PricingService.#instance;
  }
  quote(netCents: number): number {
    return this.#calculator.priceWithTax(netCents);
  }
}

// --- Fix: the behaviour, with nothing around it ---
const VAT_RATE = 0.23;
function priceWithTax(netCents: number): number {
  return Math.round(netCents * (1 + VAT_RATE));
}

// --- Demo ---
for (const net of [1000, 1999, 50]) {
  const before = PricingService.getInstance().quote(net);
  const after = priceWithTax(net);
  console.log(net, after, before === after ? "same" : "DIFFERENT");
}
