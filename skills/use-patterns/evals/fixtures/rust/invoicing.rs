pub trait DiscountPolicy {
    fn apply(&self, amount: f64) -> f64;
    fn describe(&self) -> String;
}

pub struct Percentage(pub f64);
pub struct FixedAmount(pub f64);
impl DiscountPolicy for Percentage {
    fn apply(&self, amount: f64) -> f64 { amount * (1.0 - self.0 / 100.0) }
    fn describe(&self) -> String { format!("{}% off", self.0) }
}

impl DiscountPolicy for FixedAmount {
    fn apply(&self, amount: f64) -> f64 { (amount - self.0).max(0.0) }
    fn describe(&self) -> String { format!("{:.2} off", self.0) }
}

pub struct Customer { pub name: String, pub channel: String, pub contact: String, pub discount: Option<Box<dyn DiscountPolicy>> }

pub fn amount_due(c: &Customer, net: f64) -> f64 {
    match &c.discount {
        Some(d) => d.apply(net),
        None => net,
    }
}

pub fn discount_note(c: &Customer) -> String {
    match &c.discount {
        Some(d) => d.describe(),
        None => String::from("no discount"),
    }
}

pub fn savings(c: &Customer, net: f64) -> f64 {
    if let Some(d) = &c.discount { net - d.apply(net) } else { 0.0 }
}

pub struct Invoice {
    pub id: String, pub currency: String, pub due_days: u32,
    pub po_number: Option<String>, pub notes: Option<String>, pub reverse_charge: bool,
    pub lines: Vec<(String, f64)>,
}

impl Invoice {
    pub fn new(id: &str, currency: &str, due_days: u32, po_number: Option<&str>, notes: Option<&str>, reverse_charge: bool, lines: Vec<(String, f64)>) -> Self {
        Invoice { id: id.into(), currency: currency.into(), due_days, po_number: po_number.map(String::from), notes: notes.map(String::from), reverse_charge, lines }
    }
    pub fn net(&self) -> f64 { self.lines.iter().map(|(_, amount)| amount).sum() }
}

pub fn symbol(currency: &str) -> &'static str {
    match currency {
        "EUR" => "€",
        "USD" => "$",
        "GBP" => "£",
        _ => "¤",
    }
}

pub fn late_fee(net: f64, business: bool) -> f64 { if business { net * 0.02 } else { 5.0 } }

pub trait TaxRule { fn tax(&self, net: f64) -> f64; }
pub struct VatRule { pub rate: f64 }
impl TaxRule for VatRule { fn tax(&self, net: f64) -> f64 { net * self.rate } }

pub fn gross(inv: &Invoice, rule: &dyn TaxRule) -> f64 {
    if inv.reverse_charge { inv.net() } else { inv.net() + rule.tax(inv.net()) }
}

fn main() {
    let lines = vec![("Consulting".to_string(), 1200.0), ("Travel".to_string(), 180.0)];
    let a = Invoice::new("INV-1", "EUR", 30, None, None, false, lines.clone());
    let b = Invoice::new("INV-2", "USD", 14, Some("PO-77"), None, true, lines);
    let acme = Customer { name: "Acme".into(), channel: "email".into(), contact: "ap@acme.test".into(), discount: Some(Box::new(Percentage(5.0))) };
    let globex = Customer { name: "Globex".into(), channel: "sms".into(), contact: "+351900000000".into(), discount: None };
    let vat = VatRule { rate: 0.23 };
    println!("{} {}{:.2} {}", a.id, symbol(&a.currency), gross(&a, &vat), discount_note(&acme));
    println!("{} {}{:.2} {:.2}", b.id, symbol(&b.currency), gross(&b, &vat), savings(&globex, b.net()));
    println!("{}", messaging::send_invoice(&acme, &a));
    println!("{}", messaging::send_reminder(&globex, &b, 12));
    let mut ledger = messaging::Ledger::default();
    ledger.post_payment(&a.id, amount_due(&acme, a.net()));
    ledger.post_refund(&a.id, late_fee(a.net(), true));
    println!("{:?} {:.2} {:.2} {:?}", b.po_number, ledger.balance, ledger.dashboard.received, ledger.outbox.queued);
    extras::run(&a, &b, &acme);
}

mod messaging;

mod extras {
    use crate::{Customer, Invoice};
    use std::collections::HashMap;

    pub const PAYMENT_TERMS_DAYS: u32 = 30;
    pub const MAX_LINES_PER_INVOICE: usize = 30;

    pub fn vat_line(net: f64) -> String { format!("VAT 23%: {:.2}", net * 0.23) }
    pub fn price_with_vat(net: f64) -> f64 { net * 1.23 }

    pub fn reminder_text(inv: &Invoice, days_late: u32, c: &Customer) -> Option<String> {
        if days_late > 0 {
            if !inv.reverse_charge {
                if let Some(po) = &inv.po_number {
                    if days_late > PAYMENT_TERMS_DAYS {
                        Some(format!("{}: final notice for {} (PO {po})", c.name, inv.id))
                    } else {
                        Some(format!("{}: {} is overdue (PO {po})", c.name, inv.id))
                    }
                } else if days_late > PAYMENT_TERMS_DAYS {
                    Some(format!("{}: final notice for {}", c.name, inv.id))
                } else {
                    None
                }
            } else {
                None
            }
        } else {
            None
        }
    }

    pub trait InvoiceStore {
        fn get(&self, id: &str) -> Option<&String>;
        fn put(&mut self, id: &str, body: String);
        fn delete(&mut self, id: &str);
        fn overdue(&self, today: u32) -> Vec<String>;
        fn export_csv(&self) -> String;
    }

    #[derive(Default)]
    pub struct MemoryStore { rows: HashMap<String, (String, u32)> }

    impl InvoiceStore for MemoryStore {
        fn get(&self, id: &str) -> Option<&String> { self.rows.get(id).map(|(body, _)| body) }
        fn put(&mut self, id: &str, body: String) { self.rows.insert(id.into(), (body, 0)); }
        fn delete(&mut self, id: &str) { self.rows.remove(id); }
        fn overdue(&self, today: u32) -> Vec<String> { self.rows.iter().filter(|(_, (_, due))| *due < today).map(|(id, _)| id.clone()).collect() }
        fn export_csv(&self) -> String { self.rows.keys().cloned().collect::<Vec<_>>().join(",") }
    }

    #[derive(Default)]
    pub struct ArchiveStore { ids: Vec<String> }

    impl InvoiceStore for ArchiveStore {
        fn get(&self, _id: &str) -> Option<&String> { unimplemented!("the archive is write-only") }
        fn put(&mut self, id: &str, _body: String) { self.ids.push(id.into()) }
        fn delete(&mut self, _id: &str) { unimplemented!("the archive is append-only") }
        fn overdue(&self, _today: u32) -> Vec<String> { Vec::new() }
        fn export_csv(&self) -> String { self.ids.join(",") }
    }

    pub fn archive_all(store: &mut dyn InvoiceStore, invoices: &[&Invoice]) {
        for inv in invoices {
            store.put(&inv.id, format!("{} {:.2}", inv.currency, inv.net()));
        }
    }

    #[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
    pub struct Cents(pub i64);

    impl Cents {
        pub fn from_units(units: f64) -> Self { Cents((units * 100.0).round() as i64) }
        pub fn add(self, o: Cents) -> Cents { Cents(self.0 + o.0) }
        pub fn sub(self, o: Cents) -> Cents { Cents(self.0 - o.0) }
        pub fn times(self, n: i64) -> Cents { Cents(self.0 * n) }
        pub fn percent(self, pct: i64) -> Cents { Cents(self.0 * pct / 100) }
        pub fn is_zero(self) -> bool { self.0 == 0 }
        pub fn split(self, parts: i64) -> Vec<Cents> { (0..parts).map(|i| Cents(self.0 / parts + i64::from(i < self.0 % parts))).collect() }
        pub fn display(self) -> String { format!("{}.{:02}", self.0 / 100, self.0 % 100) }
    }

    pub fn run(a: &Invoice, b: &Invoice, c: &Customer) {
        let mut memory = MemoryStore::default();
        let mut archive = ArchiveStore::default();
        archive_all(&mut memory, &[a, b]);
        archive_all(&mut archive, &[a, b]);
        memory.delete(&b.id);
        println!("{} {:.2} {:?} {:?}", vat_line(a.net()), price_with_vat(a.net()), reminder_text(b, 45, c), memory.get(&a.id));
        println!("{} {} {:?} {}", memory.export_csv(), archive.export_csv(), memory.overdue(1), MAX_LINES_PER_INVOICE);
        let total = Cents::from_units(a.net()).add(Cents(250)).sub(Cents(50)).times(2).percent(50);
        println!("{} {} {:?}", total.display(), total.is_zero(), total.split(3));
    }
}
