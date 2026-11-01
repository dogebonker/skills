// Decorator: generic wrappers implementing the same trait, stacked at compile time.
trait DataSource {
    fn read(&self) -> String;
}

struct FileSource(&'static str);
impl DataSource for FileSource {
    fn read(&self) -> String {
        self.0.to_string()
    }
}

struct Uppercase<D: DataSource>(D);
impl<D: DataSource> DataSource for Uppercase<D> {
    fn read(&self) -> String {
        self.0.read().to_uppercase()
    }
}

struct Reversed<D: DataSource>(D);
impl<D: DataSource> DataSource for Reversed<D> {
    fn read(&self) -> String {
        self.0.read().chars().rev().collect()
    }
}

fn main() {
    let plain = FileSource("payload");
    println!("{}", plain.read());

    // The stack's type is Reversed<Uppercase<FileSource>>, no heap allocation.
    let stacked = Reversed(Uppercase(FileSource("payload")));
    println!("{}", stacked.read());
}
