export {};

// Adapter: wrap a legacy gateway so it satisfies the PaymentProcessor interface callers expect.
interface PaymentProcessor {
  pay(amountCents: number, currency: string): Promise<{ ok: boolean; id: string }>;
}

class LegacyGateway {
  charge(dollars: string, cur: string): { status: "APPROVED" | "DECLINED"; ref: string } {
    return { status: Number(dollars) > 0 ? "APPROVED" : "DECLINED", ref: `LG-${cur}-${dollars}` };
  }
}

class LegacyGatewayAdapter implements PaymentProcessor {
  readonly #gateway: LegacyGateway;

  constructor(gateway: LegacyGateway) {
    this.#gateway = gateway;
  }

  async pay(amountCents: number, currency: string) {
    const result = this.#gateway.charge((amountCents / 100).toFixed(2), currency);
    return { ok: result.status === "APPROVED", id: result.ref };
  }
}

async function checkout(processor: PaymentProcessor): Promise<void> {
  console.log(await processor.pay(1999, "EUR"));
}

checkout(new LegacyGatewayAdapter(new LegacyGateway())).catch(console.error);
