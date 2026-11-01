// SRP: one unit per reason to change. Both versions print the same invoice.

import kotlin.math.roundToLong

data class Line(val sku: String, val qty: Int, val unitCents: Long)

// --- Violation: tax maths (finance), layout (product) and storage (ops) share one class.
class InvoiceServiceV1 {
    private val saved = mutableMapOf<String, String>()

    fun issue(id: String, lines: List<Line>, vatRate: Double): String {
        val net = lines.sumOf { it.qty * it.unitCents }
        val total = (net * (1 + vatRate)).roundToLong()
        val text = (lines.map { "${it.sku} x${it.qty}" } + "TOTAL %.2f".format(java.util.Locale.ROOT, total / 100.0)).joinToString("\n")
        saved[id] = text
        return text
    }
}

// --- Fix: one function per reason to change; storage is its own small class.
fun invoiceTotalCents(lines: List<Line>, vatRate: Double): Long =
    (lines.sumOf { it.qty * it.unitCents } * (1 + vatRate)).roundToLong()

fun renderInvoice(lines: List<Line>, totalCents: Long): String =
    (lines.map { "${it.sku} x${it.qty}" } + "TOTAL %.2f".format(java.util.Locale.ROOT, totalCents / 100.0)).joinToString("\n")

class InvoiceArchive {
    private val saved = mutableMapOf<String, String>()

    fun save(id: String, text: String) {
        saved[id] = text
    }

    val size: Int get() = saved.size
}

fun issueInvoice(id: String, lines: List<Line>, vatRate: Double, archive: InvoiceArchive): String {
    val text = renderInvoice(lines, invoiceTotalCents(lines, vatRate))
    archive.save(id, text)
    return text
}

fun main() {
    val lines = listOf(Line("KB-101", 2, 4999), Line("MS-220", 1, 2450))
    val before = InvoiceServiceV1().issue("INV-1", lines, 0.2)
    val archive = InvoiceArchive()
    val after = issueInvoice("INV-1", lines, 0.2, archive)
    println("violation:\n$before")
    println("fix:\n$after")
    println("same output: ${before == after} | archived: ${archive.size}")
}
