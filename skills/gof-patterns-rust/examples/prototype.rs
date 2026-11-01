// Prototype: derive Clone. Clone is deep for owned data, so a copy is independent.
use std::collections::HashMap;

#[derive(Clone, Debug)]
struct InvoiceTemplate {
    currency: String,
    lines: Vec<String>,
    meta: HashMap<String, String>,
}

fn main() {
    let mut base = InvoiceTemplate {
        currency: "EUR".into(),
        lines: vec!["Hosting".into()],
        meta: HashMap::from([("terms".to_string(), "net30".to_string())]),
    };

    // Each customer starts from a clone of the prototype.
    let mut acme = base.clone();
    acme.lines.push("Support".into());
    acme.meta.insert("customer".into(), "acme".into());

    // Changing the original afterwards does not affect the copy.
    base.currency = "USD".into();

    println!("base: {} {:?}", base.currency, base.lines);
    println!(
        "acme: {} {:?} {}",
        acme.currency, acme.lines, acme.meta["customer"]
    );
}
