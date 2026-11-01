pub trait Deduction {
    fn label(&self) -> String;
    fn amount(&self, gross: f64) -> f64;
}

pub struct PensionContribution {
    pub percent: f64,
}

impl Deduction for PensionContribution {
    fn label(&self) -> String {
        format!("Pension {}%", self.percent)
    }

    fn amount(&self, gross: f64) -> f64 {
        gross * self.percent / 100.0
    }
}

pub fn round_cents(amount: f64) -> i64 {
    if !amount.is_finite() {
        return 0;
    }
    (amount * 100.0).round() as i64
}

pub fn money(amount: f64) -> String {
    let cents = round_cents(amount);
    format!("{}.{:02}", cents / 100, cents.rem_euclid(100))
}
