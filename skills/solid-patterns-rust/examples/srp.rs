// SRP in Rust: split by reason to change into modules. Each module would be
// its own file (payroll.rs, reporting.rs, storage.rs) in a real crate.

#[derive(Debug, Clone)]
struct Employee {
    name: String,
    hourly_cents: u64,
    hours: u32,
}

// --- Violation: one impl serves three groups. Finance edits pay rules,
// operations edits the hours report, the platform team edits storage.
impl Employee {
    fn pay_cents(&self) -> u64 {
        let base = self.hours.min(40) as u64 * self.hourly_cents;
        let overtime = self.hours.saturating_sub(40) as u64 * self.hourly_cents * 3 / 2;
        base + overtime
    }

    fn hours_report(&self) -> String {
        format!("{:<6} {:>3}h", self.name, self.hours)
    }

    fn to_row(&self) -> String {
        format!("{};{};{}", self.name, self.hourly_cents, self.hours)
    }
}

// --- Fix: the data stays plain; each module owns one reason to change.
mod payroll {
    use super::Employee;

    pub fn pay_cents(e: &Employee) -> u64 {
        let base = e.hours.min(40) as u64 * e.hourly_cents;
        let overtime = e.hours.saturating_sub(40) as u64 * e.hourly_cents * 3 / 2;
        base + overtime
    }
}

mod reporting {
    use super::Employee;

    pub fn hours_line(e: &Employee) -> String {
        format!("{:<6} {:>3}h", e.name, e.hours)
    }
}

mod storage {
    use super::Employee;

    pub fn to_row(e: &Employee) -> String {
        format!("{};{};{}", e.name, e.hourly_cents, e.hours)
    }
}

fn main() {
    let staff = vec![
        Employee {
            name: "Ana".into(),
            hourly_cents: 3000,
            hours: 38,
        },
        Employee {
            name: "Bruno".into(),
            hourly_cents: 2500,
            hours: 46,
        },
    ];
    for e in &staff {
        let before = (e.pay_cents(), e.hours_report(), e.to_row());
        let after = (
            payroll::pay_cents(e),
            reporting::hours_line(e),
            storage::to_row(e),
        );
        println!("{} | pay {} | row {}", after.1, after.0, after.2);
        println!("same output: {}", before == after);
    }
}
