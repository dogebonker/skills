// Facade: one struct owns the subsystems and exposes a single simple method.
struct Inventory;
struct Payments;
struct Shipping;

impl Inventory {
    fn reserve(&self, sku: &str, qty: u32) -> Result<(), String> {
        if qty > 10 {
            Err(format!("not enough {sku}"))
        } else {
            Ok(())
        }
    }
    fn release(&self, sku: &str, qty: u32) {
        println!("released {sku} x{qty}");
    }
}
impl Payments {
    fn charge(&self, cents: u64) -> Result<String, String> {
        if cents > 100_000 {
            return Err("card declined".into());
        }
        Ok(format!("txn-{cents}"))
    }
}
impl Shipping {
    fn schedule(&self, sku: &str) -> String {
        format!("shipment for {sku}")
    }
}

struct OrderFacade {
    inventory: Inventory,
    payments: Payments,
    shipping: Shipping,
}

impl OrderFacade {
    fn new() -> Self {
        OrderFacade {
            inventory: Inventory,
            payments: Payments,
            shipping: Shipping,
        }
    }
    // Callers use only this; `?` hides the error plumbing between subsystems.
    fn place_order(&self, sku: &str, qty: u32, unit_cents: u64) -> Result<String, String> {
        if qty == 0 {
            return Err("quantity must be greater than 0".into());
        }
        // Validate everything before the first committed step.
        let total = unit_cents
            .checked_mul(u64::from(qty))
            .ok_or_else(|| "amount overflow".to_string())?;
        self.inventory.reserve(sku, qty)?;
        let txn = match self.payments.charge(total) {
            Ok(txn) => txn,
            Err(e) => {
                self.inventory.release(sku, qty); // compensate the committed step
                return Err(e);
            }
        };
        Ok(format!("{txn}, {}", self.shipping.schedule(sku)))
    }
}

fn main() {
    let shop = OrderFacade::new();
    println!("{:?}", shop.place_order("book", 2, 1500));
    println!("{:?}", shop.place_order("book", 50, 1500));
    println!("{:?}", shop.place_order("book", 0, 1500));
    println!("{:?}", shop.place_order("tv", 2, 60_000)); // charge fails, stock released
}
