// Strategy: pass a closure or fn item. Generic F gives static dispatch; no trait object needed.
fn shipping_flat(_weight_g: u32) -> u64 {
    500
}

fn shipping_by_weight(weight_g: u32) -> u64 {
    200 + weight_g as u64 / 10
}

struct Cart {
    weight_g: u32,
    subtotal: u64,
}

impl Cart {
    fn total<F: Fn(u32) -> u64>(&self, shipping: F) -> u64 {
        self.subtotal + shipping(self.weight_g)
    }
}

fn main() {
    let cart = Cart {
        weight_g: 2500,
        subtotal: 4000,
    };
    println!("flat:   {}", cart.total(shipping_flat));
    println!("weight: {}", cart.total(shipping_by_weight));

    // A closure capturing local state is also a strategy.
    let free_over = 3000;
    let promo = |w| {
        if cart.subtotal >= free_over {
            0
        } else {
            shipping_by_weight(w)
        }
    };
    println!("promo:  {}", cart.total(promo));
}
