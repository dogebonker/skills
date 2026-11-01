// Abstract Factory: one factory per region creates a matching family of tax and invoice objects.

interface TaxCalculator {
    fun taxFor(amount: Double): Double
}

interface InvoiceFormatter {
    fun format(amount: Double, tax: Double): String
}

interface RegionFactory {
    fun createTax(): TaxCalculator
    fun createFormatter(): InvoiceFormatter
}

class EuFactory : RegionFactory {
    override fun createTax() = object : TaxCalculator {
        override fun taxFor(amount: Double) = amount * 0.23
    }

    override fun createFormatter() = object : InvoiceFormatter {
        override fun format(amount: Double, tax: Double) = "EUR %.2f (VAT %.2f)".format(amount, tax)
    }
}

class UsFactory : RegionFactory {
    override fun createTax() = object : TaxCalculator {
        override fun taxFor(amount: Double) = amount * 0.07
    }

    override fun createFormatter() = object : InvoiceFormatter {
        override fun format(amount: Double, tax: Double) = "USD %.2f (sales tax %.2f)".format(amount, tax)
    }
}

// Client code only sees the abstract types, so a family can never be mixed up.
fun invoiceLine(factory: RegionFactory, amount: Double): String {
    val tax = factory.createTax().taxFor(amount)
    return factory.createFormatter().format(amount, tax)
}

fun main() {
    println(invoiceLine(EuFactory(), 100.0))
    println(invoiceLine(UsFactory(), 100.0))
}
