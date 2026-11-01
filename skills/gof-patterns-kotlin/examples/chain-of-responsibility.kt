// Chain of Responsibility: each handler either answers or passes the request to the next one.

data class Request(val user: String?, val amountCents: Long)

abstract class Handler(private val next: Handler? = null) {
    // Returns null when the request passes every check.
    open fun handle(request: Request): String? = next?.handle(request)
}

class AmountCheck(next: Handler? = null) : Handler(next) {
    override fun handle(request: Request) =
        if (request.amountCents <= 0) "rejected: amount must be positive" else super.handle(request)
}

class AuthCheck(next: Handler? = null) : Handler(next) {
    override fun handle(request: Request) =
        if (request.user == null) "rejected: not logged in" else super.handle(request)
}

class LimitCheck(private val limit: Long, next: Handler? = null) : Handler(next) {
    override fun handle(request: Request) =
        if (request.amountCents > limit) "rejected: over limit" else super.handle(request)
}

class Approve : Handler() {
    override fun handle(request: Request) = "approved ${request.amountCents} for ${request.user}"
}

// The same chain as a list of functions, which is often enough:
val checks: List<(Request) -> String?> = listOf(
    { r -> if (r.amountCents <= 0) "rejected: amount must be positive" else null },
    { r -> if (r.user == null) "rejected: not logged in" else null },
    { r -> if (r.amountCents > 5_000) "rejected: over limit" else null },
)

fun main() {
    val chain = AmountCheck(AuthCheck(LimitCheck(5_000, Approve())))
    println(chain.handle(Request("ana", 0)))
    println(chain.handle(Request(null, 100)))
    println(chain.handle(Request("ana", 9_000)))
    println(chain.handle(Request("ana", 1_000)))
    println(checks.firstNotNullOfOrNull { it(Request("ben", 9_000)) })
    println(checks.firstNotNullOfOrNull { it(Request("ben", -5)) })
}
