// Template Method: a trait's provided method fixes the algorithm; implementors fill the steps.
trait ReportJob {
    fn fetch(&self) -> Vec<u32>;
    fn format_row(&self, value: u32) -> String;

    // Hook with a default; implementors may override.
    fn header(&self) -> String {
        "REPORT".to_string()
    }

    // The template. Not meant to be overridden.
    fn run(&self) -> String {
        let rows: Vec<String> = self
            .fetch()
            .into_iter()
            .map(|v| self.format_row(v))
            .collect();
        format!("{}\n{}", self.header(), rows.join("\n"))
    }
}

struct Sales;
struct Refunds;

impl ReportJob for Sales {
    fn fetch(&self) -> Vec<u32> {
        vec![120, 80]
    }
    fn format_row(&self, value: u32) -> String {
        format!("sale   {value:>5}")
    }
}

impl ReportJob for Refunds {
    fn fetch(&self) -> Vec<u32> {
        vec![15]
    }
    fn format_row(&self, value: u32) -> String {
        format!("refund {value:>5}")
    }
    fn header(&self) -> String {
        "REFUND REPORT".to_string()
    }
}

fn main() {
    println!("{}", Sales.run());
    println!("{}", Refunds.run());
}
