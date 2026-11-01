// Proxy: a lazy, caching stand-in with the same trait as the real service.
use std::cell::RefCell;
use std::collections::HashMap;

trait PriceService {
    fn price(&self, sku: &str) -> u64;
}

struct RemotePriceService;
impl PriceService for RemotePriceService {
    fn price(&self, sku: &str) -> u64 {
        println!("  remote call for {sku}");
        sku.len() as u64 * 100
    }
}

struct CachingProxy<S: PriceService> {
    inner: S,
    // price() takes &self like the trait, so the cache needs interior mutability.
    cache: RefCell<HashMap<String, u64>>,
}

impl<S: PriceService> CachingProxy<S> {
    fn new(inner: S) -> Self {
        CachingProxy {
            inner,
            cache: RefCell::new(HashMap::new()),
        }
    }
}

impl<S: PriceService> PriceService for CachingProxy<S> {
    fn price(&self, sku: &str) -> u64 {
        if let Some(&p) = self.cache.borrow().get(sku) {
            return p;
        }
        let p = self.inner.price(sku); // no borrow is held across this call
        self.cache.borrow_mut().insert(sku.to_string(), p);
        p
    }
}

fn main() {
    let svc = CachingProxy::new(RemotePriceService);
    for sku in ["lamp", "desk", "lamp"] {
        println!("{sku}: {}", svc.price(sku));
    }
}
