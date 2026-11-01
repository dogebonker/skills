// Singleton: a static OnceLock initialised on first use; interior mutability via Mutex.
use std::sync::{Mutex, OnceLock};

struct Config {
    region: String,
    requests: Mutex<u32>,
}

fn config() -> &'static Config {
    static INSTANCE: OnceLock<Config> = OnceLock::new();
    INSTANCE.get_or_init(|| {
        println!("initialising config");
        Config {
            region: "eu-west-1".into(),
            requests: Mutex::new(0),
        }
    })
}

impl Config {
    fn record_request(&self) -> u32 {
        let mut n = self.requests.lock().unwrap();
        *n += 1;
        *n
    }
}

fn main() {
    let a = config();
    let b = config();
    println!("same instance: {}", std::ptr::eq(a, b));
    a.record_request();
    println!("region {} requests {}", b.region, b.record_request());
}
