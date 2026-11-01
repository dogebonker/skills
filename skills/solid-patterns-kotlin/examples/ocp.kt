// OCP: add a payment method without editing the fee calculation. Both versions agree.

import kotlin.math.roundToLong

data class Payment(val method: String, val amountCents: Long)

// --- Violation: every new payment method is another edit to this when.
fun feeCentsV1(p: Payment): Long = when (p.method) {
    "card" -> (p.amountCents * 0.029).roundToLong() + 30
    "bank" -> 50L
    "wallet" -> (p.amountCents * 0.015).roundToLong()
    else -> throw IllegalArgumentException("unknown payment method: ${p.method}")
}

// --- Fix: fee rules are a map of functions; feeCents stays closed, the map is open.
typealias FeeRule = (amountCents: Long) -> Long

val defaultFeeRules: Map<String, FeeRule> = mapOf(
    "card" to { cents: Long -> (cents * 0.029).roundToLong() + 30 },
    "bank" to { _: Long -> 50L },
    "wallet" to { cents: Long -> (cents * 0.015).roundToLong() },
)

fun feeCents(p: Payment, rules: Map<String, FeeRule> = defaultFeeRules): Long {
    val rule = rules[p.method] ?: throw IllegalArgumentException("unknown payment method: ${p.method}")
    return rule(p.amountCents)
}

fun main() {
    for (method in listOf("card", "bank", "wallet")) {
        val p = Payment(method, 12000)
        println("$method violation: ${feeCentsV1(p)} fix: ${feeCents(p)} same output: ${feeCentsV1(p) == feeCents(p)}")
    }
    // Extension: a new method is a new entry passed in by the caller. feeCents is untouched.
    val withVoucher = defaultFeeRules + ("voucher" to { _: Long -> 0L })
    println("voucher fix: ${feeCents(Payment("voucher", 12000), withVoucher)}")
}
