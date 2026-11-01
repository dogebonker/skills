// DIP in Rust: the policy module owns the trait; the detail implements it;
// main picks the concrete type. Generics keep it statically dispatched.

mod supplier_http {
    // Stands in for an HTTP client to a supplier API.
    #[derive(Default)]
    pub struct HttpSupplier {
        pub sent: Vec<String>,
    }

    impl HttpSupplier {
        pub fn post_order(&mut self, sku: &str, qty: u32) -> String {
            let id = format!("PO-{}-{sku}x{qty}", self.sent.len() + 1);
            self.sent.push(id.clone());
            id
        }
    }

    // The adapter sits on the detail side and points at the policy's trait.
    impl crate::policy::Supplier for HttpSupplier {
        fn place_order(&mut self, sku: &str, qty: u32) -> String {
            self.post_order(sku, qty)
        }
    }
}

// --- Violation: the reorder policy builds and names its HTTP client, so it
// cannot run without that detail and cannot be tested in isolation.
mod policy_v1 {
    use crate::supplier_http::HttpSupplier;

    pub struct ReorderPolicy {
        pub supplier: HttpSupplier,
    }

    impl ReorderPolicy {
        pub fn new() -> Self {
            ReorderPolicy {
                supplier: HttpSupplier::default(),
            }
        }

        pub fn check(&mut self, sku: &str, on_hand: u32) -> Option<String> {
            (on_hand < 10).then(|| self.supplier.post_order(sku, 50 - on_hand))
        }
    }
}

// --- Fix: the trait lives with the policy. The detail depends on it.
mod policy {
    pub trait Supplier {
        fn place_order(&mut self, sku: &str, qty: u32) -> String;
    }

    pub struct ReorderPolicy<S: Supplier> {
        supplier: S,
    }

    impl<S: Supplier> ReorderPolicy<S> {
        pub fn new(supplier: S) -> Self {
            ReorderPolicy { supplier }
        }

        pub fn check(&mut self, sku: &str, on_hand: u32) -> Option<String> {
            (on_hand < 10).then(|| self.supplier.place_order(sku, 50 - on_hand))
        }
    }
}

fn main() {
    let stock = [("KB-101", 4), ("MS-220", 30), ("HD-330", 9)];

    let mut before = policy_v1::ReorderPolicy::new();
    let mut after = policy::ReorderPolicy::new(supplier_http::HttpSupplier::default());
    for (sku, on_hand) in stock {
        let (a, b) = (before.check(sku, on_hand), after.check(sku, on_hand));
        println!("{sku}: {b:?} same output: {}", a == b);
    }
}
