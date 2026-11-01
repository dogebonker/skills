// ISP in Rust: small traits, combined with `+` where a caller needs more
// than one. No implementer is forced to stub a method it cannot support.

#[derive(Debug, PartialEq)]
enum Job {
    Printed(String),
    Scanned(String),
}

// --- Violation: one fat trait. A basic printer must implement scan and
// fax, and does so with stubs that only fail at runtime.
trait OfficeDeviceV1 {
    fn print(&mut self, doc: &str) -> Job;
    fn scan(&mut self, page: &str) -> Result<Job, String>;
    fn fax(&mut self, number: &str, doc: &str) -> Result<(), String>;
}

struct BasicPrinterV1;
impl OfficeDeviceV1 for BasicPrinterV1 {
    fn print(&mut self, doc: &str) -> Job {
        Job::Printed(doc.to_uppercase())
    }
    fn scan(&mut self, _page: &str) -> Result<Job, String> {
        Err("this printer has no scanner".into())
    }
    fn fax(&mut self, _number: &str, _doc: &str) -> Result<(), String> {
        Err("this printer has no fax".into())
    }
}

fn print_invoices_v1(device: &mut impl OfficeDeviceV1, invoices: &[&str]) -> Vec<Job> {
    invoices.iter().map(|i| device.print(i)).collect()
}

// --- Fix: one trait per capability. Callers ask only for what they use.
trait Print {
    fn print(&mut self, doc: &str) -> Job;
}
trait Scan {
    fn scan(&mut self, page: &str) -> Job;
}

struct BasicPrinter;
impl Print for BasicPrinter {
    fn print(&mut self, doc: &str) -> Job {
        Job::Printed(doc.to_uppercase())
    }
}

struct MultiFunction;
impl Print for MultiFunction {
    fn print(&mut self, doc: &str) -> Job {
        Job::Printed(doc.to_uppercase())
    }
}
impl Scan for MultiFunction {
    fn scan(&mut self, page: &str) -> Job {
        Job::Scanned(page.to_lowercase())
    }
}

fn print_invoices(device: &mut impl Print, invoices: &[&str]) -> Vec<Job> {
    invoices.iter().map(|i| device.print(i)).collect()
}

// A caller that needs both says so in the bound.
fn copy_page(device: &mut (impl Print + Scan), page: &str) -> Job {
    match device.scan(page) {
        Job::Scanned(text) => device.print(&text),
        other => other,
    }
}

fn main() {
    let invoices = ["inv-001", "inv-002"];
    let before = print_invoices_v1(&mut BasicPrinterV1, &invoices);
    let after = print_invoices(&mut BasicPrinter, &invoices);
    println!("{after:?}");
    println!("same output: {}", before == after);
    println!("copy: {:?}", copy_page(&mut MultiFunction, "Receipt-17"));

    // What the fat trait forced BasicPrinterV1 to ship:
    let mut v1 = BasicPrinterV1;
    println!(
        "v1 stubs: {:?} {:?}",
        v1.scan("p1"),
        v1.fax("555-0100", "inv-001")
    );
}
