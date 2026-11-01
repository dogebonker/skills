// Bridge: Report (abstraction) and Output (implementation) vary independently.

interface Output {
    fun write(title: String, lines: List<String>): String
}

class PlainOutput : Output {
    override fun write(title: String, lines: List<String>) =
        (listOf(title) + lines).joinToString("\n")
}

class MarkdownOutput : Output {
    override fun write(title: String, lines: List<String>) =
        "# $title\n" + lines.joinToString("\n") { "- $it" }
}

abstract class Report(protected val output: Output) {
    abstract fun render(): String
}

class SalesReport(output: Output, private val totals: Map<String, Int>) : Report(output) {
    override fun render() =
        output.write("Sales", totals.map { (region, total) -> "$region: $total" })
}

class ErrorReport(output: Output, private val errors: List<String>) : Report(output) {
    override fun render() = output.write("Errors", errors)
}

fun main() {
    val sales = mapOf("EU" to 120, "US" to 90)
    println(SalesReport(PlainOutput(), sales).render())
    println(SalesReport(MarkdownOutput(), sales).render())
    println(ErrorReport(MarkdownOutput(), listOf("timeout", "bad card")).render())
}
