package gym.billing

interface PriceRule {
    fun price(baseCents: Long): Long
}

class MemberRate(private val discountPercent: Int) : PriceRule {
    override fun price(baseCents: Long): Long = baseCents * (100 - discountPercent) / 100
}

fun formatEuros(cents: Long): String {
    require(cents >= 0) { "negative amount $cents" }
    return "EUR %d.%02d".format(cents / 100, cents % 100)
}

fun invoiceLine(label: String, cents: Long): String = "$label: ${formatEuros(cents)}"
