// Builder: named and default arguments cover most cases; a type-safe DSL covers nested setup.

data class HttpRequest(
    val url: String,
    val method: String = "GET",
    val headers: Map<String, String> = emptyMap(),
    val timeoutMs: Int = 10_000,
)

// Step 1: often all you need. No builder class at all.
val simple = HttpRequest(url = "https://api.example.com/orders", timeoutMs = 2_000)

// Step 2: a DSL builder for when construction has steps, validation or nesting.
class RequestBuilder(private val url: String) {
    var method: String = "GET"
    var timeoutMs: Int = 10_000
    private val headers = mutableMapOf<String, String>()

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun build(): HttpRequest {
        require(url.startsWith("https://")) { "https only: $url" }
        return HttpRequest(url, method, headers.toMap(), timeoutMs)
    }
}

fun request(url: String, init: RequestBuilder.() -> Unit): HttpRequest =
    RequestBuilder(url).apply(init).build()

fun main() {
    println(simple)
    val post = request("https://api.example.com/payments") {
        method = "POST"
        header("Authorization", "Bearer token")
        header("Content-Type", "application/json")
    }
    println(post)
}
