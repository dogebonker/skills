// Composite: files and folders share one sealed type, so callers treat a tree like a leaf.

sealed interface Entry {
    val name: String
    fun size(): Long
    fun print(indent: String = "")
}

class FileEntry(override val name: String, private val bytes: Long) : Entry {
    override fun size() = bytes
    override fun print(indent: String) = println("$indent$name (${size()} B)")
}

class Folder(override val name: String, private val children: List<Entry>) : Entry {
    constructor(name: String, vararg children: Entry) : this(name, children.toList())

    override fun size(): Long = children.sumOf { it.size() }

    override fun print(indent: String) {
        println("$indent$name/ (${size()} B)")
        for (child in children) child.print("$indent  ")   // no type checks: each node prints itself
    }
}

fun main() {
    val root = Folder(
        "downloads",
        FileEntry("invoice.pdf", 1_200),
        Folder("photos", FileEntry("a.jpg", 3_000), FileEntry("b.jpg", 4_500)),
    )
    root.print()
    println("total = ${root.size()}")
}
