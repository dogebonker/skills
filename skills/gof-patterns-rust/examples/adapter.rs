// Adapter: wrap the foreign type in a newtype and implement our trait; From does the conversion.
trait PaymentGateway {
    fn charge(&self, cents: u64) -> Result<String, String>;
}

// Third-party client we cannot change: takes dollars as f64.
struct LegacyBank;
impl LegacyBank {
    fn debit(&self, dollars: f64) -> bool {
        dollars < 1000.0
    }
}

struct LegacyBankAdapter(LegacyBank);

impl From<LegacyBank> for LegacyBankAdapter {
    fn from(bank: LegacyBank) -> Self {
        LegacyBankAdapter(bank)
    }
}

impl PaymentGateway for LegacyBankAdapter {
    fn charge(&self, cents: u64) -> Result<String, String> {
        if self.0.debit(cents as f64 / 100.0) {
            Ok(format!("charged {cents} cents"))
        } else {
            Err("declined".into())
        }
    }
}

fn checkout(gateway: &impl PaymentGateway, cents: u64) {
    match gateway.charge(cents) {
        Ok(msg) => println!("ok: {msg}"),
        Err(e) => println!("failed: {e}"),
    }
}

fn main() {
    let gateway: LegacyBankAdapter = LegacyBank.into();
    checkout(&gateway, 2_500);
    checkout(&gateway, 500_000);
}
