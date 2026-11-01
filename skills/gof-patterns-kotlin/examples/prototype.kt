// Prototype: a data class gives you copy(), so cloning is one call and no Cloneable is needed.

data class Address(val city: String, val street: String)

data class UserProfile(
    val name: String,
    val theme: String,
    val tags: List<String>,
    val address: Address,
)

fun main() {
    val template = UserProfile(
        name = "template",
        theme = "dark",
        tags = listOf("new"),
        address = Address("Lisbon", "Rua A"),
    )

    // copy() is shallow: tags and address are shared, which is safe because they are immutable.
    val ana = template.copy(name = "ana")
    val ben = template.copy(name = "ben", address = template.address.copy(street = "Rua B"))

    println(ana)
    println(ben)
    println("template untouched: $template")
    println("ana shares tags with template: ${ana.tags === template.tags}")
}
