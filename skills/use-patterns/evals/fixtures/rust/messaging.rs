use crate::{amount_due, Customer, Invoice};

pub trait Sender {
    fn send(&self, to: &str, body: &str) -> String;
}

struct EmailSender { from: String }
struct SmsSender { sender_id: String }
struct WebhookSender { base_url: String }

impl Sender for EmailSender {
    fn send(&self, to: &str, body: &str) -> String { format!("mail {} -> {to}: {body}", self.from) }
}
impl Sender for SmsSender {
    fn send(&self, to: &str, body: &str) -> String { format!("sms {} -> {to}: {body}", self.sender_id) }
}
impl Sender for WebhookSender {
    fn send(&self, to: &str, body: &str) -> String { format!("POST {}/{to} {body}", self.base_url) }
}

pub fn send_invoice(c: &Customer, inv: &Invoice) -> String {
    let sender: Box<dyn Sender> = match c.channel.as_str() {
        "email" => Box::new(EmailSender { from: "billing@example.com".into() }),
        "sms" => Box::new(SmsSender { sender_id: "ACME".into() }),
        "webhook" => Box::new(WebhookSender { base_url: "https://hooks.example.com".into() }),
        other => panic!("unknown channel {other}"),
    };
    sender.send(&c.contact, &format!("{}: invoice {} due in {} days, {:.2}", c.name, inv.id, inv.due_days, amount_due(c, inv.net())))
}

pub fn send_reminder(c: &Customer, inv: &Invoice, days_late: u32) -> String {
    let sender: Box<dyn Sender> = match c.channel.as_str() {
        "email" => Box::new(EmailSender { from: "billing@example.com".into() }),
        "sms" => Box::new(SmsSender { sender_id: "ACME".into() }),
        "webhook" => Box::new(WebhookSender { base_url: "https://hooks.example.com".into() }),
        other => panic!("unknown channel {other}"),
    };
    sender.send(&c.contact, &format!("{}: invoice {} is {days_late} days late", c.name, inv.id))
}

#[derive(Default)] pub struct AuditLog { pub lines: Vec<String> }
#[derive(Default)] pub struct Dashboard { pub received: f64 }
#[derive(Default)] pub struct Outbox { pub queued: Vec<String> }
impl AuditLog { pub fn record(&mut self, line: String) { self.lines.push(line) } }
impl Dashboard { pub fn add(&mut self, amount: f64) { self.received += amount } }
impl Outbox { pub fn queue(&mut self, text: String) { self.queued.push(text) } }

#[derive(Default)] pub struct Ledger { pub balance: f64, pub audit: AuditLog, pub dashboard: Dashboard, pub outbox: Outbox }

impl Ledger {
    pub fn post_payment(&mut self, invoice_id: &str, amount: f64) {
        self.balance -= amount;
        self.audit.record(format!("payment {invoice_id} {amount:.2}"));
        self.dashboard.add(amount);
        self.outbox.queue(format!("thank you for paying {invoice_id}"));
    }
    pub fn post_refund(&mut self, invoice_id: &str, amount: f64) {
        self.balance += amount;
        self.audit.record(format!("refund {invoice_id} {amount:.2}"));
        self.dashboard.add(-amount);
        self.outbox.queue(format!("refund issued for {invoice_id}"));
    }
}
