// Iterator: implement Iterable with a sequence builder and let `yield` hold the traversal state.

class Page(val title: String, val children: List<Page> = emptyList()) : Iterable<Page> {
    // Depth-first walk, computed lazily.
    override fun iterator(): Iterator<Page> = sequence {
        yield(this@Page)
        for (child in children) yieldAll(child)
    }.iterator()
}

// A custom iteration order, exposed as a Sequence.
fun Page.breadthFirst(): Sequence<Page> = sequence {
    val queue = ArrayDeque(listOf(this@breadthFirst))
    while (queue.isNotEmpty()) {
        val page = queue.removeFirst()
        yield(page)
        queue.addAll(page.children)
    }
}

fun main() {
    val site = Page(
        "home",
        listOf(
            Page("docs", listOf(Page("install"), Page("usage"))),
            Page("blog"),
        ),
    )
    println(site.map { it.title })                              // depth first
    println(site.breadthFirst().map { it.title }.toList())      // breadth first
    println(site.firstOrNull { it.title.startsWith("us") }?.title)
}
