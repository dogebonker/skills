// Visitor: with a sealed hierarchy, an exhaustive `when` in an extension function is the visitor.
// New operations are new functions, and the compiler flags any node type you forget.

sealed interface Expr
data class Num(val value: Int) : Expr
data class Add(val left: Expr, val right: Expr) : Expr
data class Mul(val left: Expr, val right: Expr) : Expr

fun Expr.eval(): Int = when (this) {
    is Num -> value
    is Add -> left.eval() + right.eval()
    is Mul -> left.eval() * right.eval()
}

fun Expr.show(): String = when (this) {
    is Num -> value.toString()
    is Add -> "(${left.show()} + ${right.show()})"
    is Mul -> "${left.show()} * ${right.show()}"
}

fun main() {
    val expr = Mul(Add(Num(2), Num(3)), Num(4))
    println("${expr.show()} = ${expr.eval()}")
}
