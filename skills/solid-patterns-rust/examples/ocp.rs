// OCP in Rust: checkout depends on a trait, so a downstream crate can add a
// payment method without editing this code. A match on a string cannot.

// --- Violation: every new method edits this match.
fn fee_cents_v1(method: &str, amount_cents: u64) -> Result<u64, String> {
    match method {
        "card" => Ok(30 + amount_cents * 29 / 1000),
        "bank_transfer" => Ok(50),
        other => Err(format!("unknown payment method {other}")),
    }
}

// --- Fix: open for new types, closed for modification.
trait PaymentMethod {
    fn name(&self) -> &str;
    fn fee_cents(&self, amount_cents: u64) -> u64;
}

struct Card;
impl PaymentMethod for Card {
    fn name(&self) -> &str {
        "card"
    }
    fn fee_cents(&self, amount_cents: u64) -> u64 {
        30 + amount_cents * 29 / 1000
    }
}

struct BankTransfer;
impl PaymentMethod for BankTransfer {
    fn name(&self) -> &str {
        "bank_transfer"
    }
    fn fee_cents(&self, _amount_cents: u64) -> u64 {
        50
    }
}

// The set is chosen at runtime and is heterogeneous, so `dyn` fits here.
fn fee_cents(
    methods: &[Box<dyn PaymentMethod>],
    name: &str,
    amount_cents: u64,
) -> Result<u64, String> {
    methods
        .iter()
        .find(|m| m.name() == name)
        .map(|m| m.fee_cents(amount_cents))
        .ok_or_else(|| format!("unknown payment method {name}"))
}

fn main() {
    // Wiring: a new method is one more Box here, plus its own type.
    let methods: Vec<Box<dyn PaymentMethod>> = vec![Box::new(Card), Box::new(BankTransfer)];
    for (name, amount) in [("card", 12_000), ("bank_transfer", 12_000), ("crypto", 500)] {
        let before = fee_cents_v1(name, amount);
        let after = fee_cents(&methods, name, amount);
        println!("{name:<13} {after:?} same output: {}", before == after);
    }
}
