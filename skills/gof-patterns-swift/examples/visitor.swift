// Visitor: an enum plus switch gives new operations without touching the node types.
enum Expr {
    case number(Double)
    indirect case add(Expr, Expr)
    indirect case multiply(Expr, Expr)
}

// Each operation is an ordinary function over the enum.
func evaluate(_ expr: Expr) -> Double {
    switch expr {
    case .number(let value): return value
    case .add(let l, let r): return evaluate(l) + evaluate(r)
    case .multiply(let l, let r): return evaluate(l) * evaluate(r)
    }
}

func render(_ expr: Expr) -> String {
    switch expr {
    case .number(let value): return "\(value)"
    case .add(let l, let r): return "(\(render(l)) + \(render(r)))"
    case .multiply(let l, let r): return "\(render(l)) * \(render(r))"
    }
}

let expr = Expr.multiply(.add(.number(2), .number(3)), .number(4))
print(render(expr), "=", evaluate(expr))
