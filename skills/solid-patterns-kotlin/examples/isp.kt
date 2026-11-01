// ISP: a client depends only on the members it calls. Both versions build the same message.

data class Customer(val id: String, val email: String, val overdue: Boolean = false)

// Kotlin interfaces are nominal: a class fits only the interfaces it declares. So the wide
// repository is composed from a small role interface, and the fix can depend on that role.
fun interface EmailLookup {
    fun findEmail(id: String): String?
}

interface CustomerRepository : EmailLookup {
    fun save(customer: Customer)
    fun remove(id: String)
    fun listOverdue(): List<Customer>
}

class InMemoryCustomerRepository : CustomerRepository {
    private val rows = mutableMapOf<String, Customer>()

    override fun findEmail(id: String): String? = rows[id]?.email

    override fun save(customer: Customer) {
        rows[customer.id] = customer
    }

    override fun remove(id: String) {
        rows.remove(id)
    }

    override fun listOverdue(): List<Customer> = rows.values.filter { it.overdue }
}

// --- Violation: needs one method but demands the whole repository.
fun welcomeMessageV1(repo: CustomerRepository, id: String): String {
    val email = repo.findEmail(id) ?: throw NoSuchElementException("no customer $id")
    return "Welcome! Receipts go to $email."
}

// --- Fix: depend on the role. A lambda satisfies a fun interface.
fun welcomeMessage(lookup: EmailLookup, id: String): String {
    val email = lookup.findEmail(id) ?: throw NoSuchElementException("no customer $id")
    return "Welcome! Receipts go to $email."
}

private fun unused(): Nothing = throw AssertionError("not used by welcomeMessage")

fun main() {
    val repo = InMemoryCustomerRepository()
    repo.save(Customer("c-7", "ana@example.com"))
    println("violation: ${welcomeMessageV1(repo, "c-7")}")
    println("fix:       ${welcomeMessage(repo, "c-7")}")
    println("same output: ${welcomeMessageV1(repo, "c-7") == welcomeMessage(repo, "c-7")}")

    // The cost shows in tests: three unused stubs against one lambda.
    val fatFake = object : CustomerRepository {
        override fun findEmail(id: String): String? = "test@example.com"
        override fun save(customer: Customer) { unused() }
        override fun remove(id: String) { unused() }
        override fun listOverdue(): List<Customer> = unused()
    }
    println("violation fake: ${welcomeMessageV1(fatFake, "x")}")
    println("fix fake:       ${welcomeMessage(EmailLookup { "test@example.com" }, "x")}")
}
