export {};

// Facade: one simple method hides three subsystems that must be called in order.
class Inventory {
  reserve(sku: string, qty: number): boolean {
    console.log(`inventory: reserved ${qty} x ${sku}`);
    return true;
  }
  release(sku: string, qty: number): void {
    console.log(`released ${sku} x ${qty}`);
  }
}
class Billing {
  charge(customer: string, cents: number): string {
    if (customer === "mallory") throw new Error("card declined");
    console.log(`billing: charged ${customer} ${cents}`);
    return "txn-1";
  }
}
class Shipping {
  schedule(customer: string, sku: string): string {
    return `shipment for ${customer}: ${sku}`;
  }
}

class OrderFacade {
  private readonly inventory = new Inventory();
  private readonly billing = new Billing();
  private readonly shipping = new Shipping();

  placeOrder(customer: string, sku: string, qty: number, priceCents: number): string {
    if (!Number.isInteger(qty) || qty <= 0) throw new RangeError("qty must be a positive integer");
    if (!Number.isFinite(priceCents) || priceCents < 0) throw new RangeError("price must be >= 0");
    if (!this.inventory.reserve(sku, qty)) throw new Error("out of stock");
    let txn: string;
    try {
      txn = this.billing.charge(customer, qty * priceCents);
    } catch (err) {
      this.inventory.release(sku, qty);
      throw err;
    }
    return `${this.shipping.schedule(customer, sku)} (${txn})`;
  }
}

const facade = new OrderFacade();
console.log(facade.placeOrder("ada", "KB-01", 2, 4500));
try {
  facade.placeOrder("mallory", "KB-01", 1, 4500);
} catch (err) {
  console.log(`failed: ${(err as Error).message}`);
}
try {
  facade.placeOrder("ada", "KB-01", 0, 4500);
} catch (err) {
  console.log(`failed: ${(err as Error).message}`);
}
