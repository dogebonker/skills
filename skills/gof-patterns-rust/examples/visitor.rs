// Visitor: for a closed set of node types, free functions with `match` are the visitor,
// and the compiler checks exhaustiveness. The trait form below earns its place when
// default methods walk the tree, so each visitor overrides only the nodes it cares about
// (as `syn::visit::Visit` does).
enum Expr {
    Num(f64),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
}

fn eval(e: &Expr) -> f64 {
    match e {
        Expr::Num(n) => *n,
        Expr::Add(l, r) => eval(l) + eval(r),
        Expr::Mul(l, r) => eval(l) * eval(r),
    }
}

fn render(e: &Expr) -> String {
    match e {
        Expr::Num(n) => n.to_string(),
        Expr::Add(l, r) => format!("({} + {})", render(l), render(r)),
        Expr::Mul(l, r) => format!("{} * {}", render(l), render(r)),
    }
}

trait Visitor {
    fn visit(&mut self, e: &Expr) {
        match e {
            Expr::Num(n) => self.visit_num(*n),
            Expr::Add(l, r) | Expr::Mul(l, r) => {
                self.visit(l);
                self.visit(r);
            }
        }
    }
    fn visit_num(&mut self, _n: f64) {}
}

// Overrides one node kind; the default `visit` does the walking.
struct SumNums(f64);
impl Visitor for SumNums {
    fn visit_num(&mut self, n: f64) {
        self.0 += n;
    }
}

fn main() {
    use Expr::*;
    let e = Mul(
        Box::new(Add(Box::new(Num(2.0)), Box::new(Num(3.0)))),
        Box::new(Num(4.0)),
    );
    println!("{} = {}", render(&e), eval(&e));
    let mut sum = SumNums(0.0);
    sum.visit(&e);
    println!("sum of literals: {}", sum.0);
}
