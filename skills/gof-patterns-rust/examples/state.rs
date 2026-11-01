// State: an enum plus match. Transitions consume the old state, so a stale value cannot be reused.
#[derive(Debug)]
enum Order {
    Pending { items: u32 },
    Paid { items: u32, txn: String },
    Shipped { tracking: String },
    Cancelled,
}

impl Order {
    fn pay(self, txn: &str) -> Order {
        match self {
            Order::Pending { items } => Order::Paid {
                items,
                txn: txn.into(),
            },
            other => {
                println!("cannot pay in state {other:?}");
                other
            }
        }
    }
    fn ship(self) -> Order {
        match self {
            Order::Paid { items, txn } => Order::Shipped {
                tracking: format!("TRK-{txn}-{items}"),
            },
            other => {
                println!("cannot ship in state {other:?}");
                other
            }
        }
    }
    fn cancel(self) -> Order {
        match self {
            Order::Pending { .. } | Order::Paid { .. } => Order::Cancelled,
            other => other,
        }
    }
}

fn main() {
    let order = Order::Pending { items: 3 };
    let order = order.ship(); // rejected: not paid yet
    let order = order.pay("42").ship();
    if let Order::Shipped { tracking } = &order {
        println!("shipped with {tracking}");
    }
    println!("{:?}", order.cancel()); // already shipped, unchanged
}
