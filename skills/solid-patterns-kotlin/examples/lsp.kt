// LSP: a subtype must keep the promises callers rely on. Checking accounts pay the same in both.

// --- Violation: FixedDepositAccountV1 is an AccountV1 but throws where AccountV1 promised to withdraw.
// Kotlin classes are final by default; `open` is the explicit invitation to substitute.
open class AccountV1(protected var balance: Long) {
    val balanceCents: Long get() = balance

    open fun withdraw(cents: Long) {
        require(cents <= balance) { "insufficient funds" }
        balance -= cents
    }
}

class FixedDepositAccountV1(balance: Long) : AccountV1(balance) {
    override fun withdraw(cents: Long) {
        throw UnsupportedOperationException("fixed deposit: withdrawals locked")
    }
}

fun payInvoiceV1(from: AccountV1, cents: Long): String {
    from.withdraw(cents)
    return "paid $cents, left ${from.balanceCents}"
}

// --- Fix: split the capability. Only types that can keep the withdraw contract implement it.
interface HasBalance {
    val balanceCents: Long
}

interface Withdrawable : HasBalance {
    fun withdraw(cents: Long)
}

class CheckingAccount(private var balance: Long) : Withdrawable {
    override val balanceCents: Long get() = balance

    override fun withdraw(cents: Long) {
        require(cents <= balance) { "insufficient funds" }
        balance -= cents
    }
}

class FixedDeposit(override val balanceCents: Long) : HasBalance

fun payFrom(from: Withdrawable, cents: Long): String {
    from.withdraw(cents)
    return "paid $cents, left ${from.balanceCents}"
}

fun main() {
    println("violation, checking: ${payInvoiceV1(AccountV1(50000), 1000)}")
    println("fix, checking:       ${payFrom(CheckingAccount(50000), 1000)}")
    println("same output: ${payInvoiceV1(AccountV1(50000), 1000) == payFrom(CheckingAccount(50000), 1000)}")
    try {
        payInvoiceV1(FixedDepositAccountV1(50000), 1000)
    } catch (e: UnsupportedOperationException) {
        println("violation, fixed deposit throws: ${e.message}")
    }
    // payFrom(FixedDeposit(50000), 1000) does not compile: FixedDeposit is not Withdrawable.
    val accounts: List<HasBalance> = listOf(FixedDeposit(50000), CheckingAccount(20000))
    println("fix, payable sources: ${accounts.filterIsInstance<Withdrawable>().map { it.javaClass.simpleName }}")
}
