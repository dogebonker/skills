// Bridge: the abstraction is generic over an implementor trait, so both vary independently.
trait Sink {
    fn write(&mut self, line: &str);
}

struct ConsoleSink;
struct MemorySink(Vec<String>);

impl Sink for ConsoleSink {
    fn write(&mut self, line: &str) {
        println!("{line}");
    }
}
impl Sink for MemorySink {
    fn write(&mut self, line: &str) {
        self.0.push(line.to_string());
    }
}

// Abstraction side: report kinds; holds any Sink.
struct Report<S: Sink> {
    sink: S,
}

impl<S: Sink> Report<S> {
    fn new(sink: S) -> Self {
        Report { sink }
    }
    fn summary(&mut self, total: u32) {
        self.sink.write(&format!("SUMMARY total={total}"));
    }
    fn detailed(&mut self, items: &[(&str, u32)]) {
        for (name, qty) in items {
            self.sink.write(&format!("  {name} x{qty}"));
        }
        self.summary(items.iter().map(|(_, q)| q).sum());
    }
}

fn main() {
    let mut console = Report::new(ConsoleSink);
    console.detailed(&[("widget", 3), ("gadget", 2)]);

    let mut memory = Report::new(MemorySink(Vec::new()));
    memory.summary(7);
    println!("captured: {:?}", memory.sink.0);
}
