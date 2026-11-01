// Command: each edit is an object with execute and undo, so history is just a stack.

class Document {
    val text = StringBuilder()
}

interface Command {
    fun execute()
    fun undo()
}

class AppendText(private val doc: Document, private val added: String) : Command {
    override fun execute() { doc.text.append(added) }
    override fun undo() { doc.text.setLength(doc.text.length - added.length) }
}

class Clear(private val doc: Document) : Command {
    private var saved = ""
    override fun execute() { saved = doc.text.toString(); doc.text.setLength(0) }
    override fun undo() { doc.text.append(saved) }
}

class History {
    private val done = ArrayDeque<Command>()

    fun run(command: Command) {
        command.execute()
        done.addLast(command)
    }

    fun undo() {
        done.removeLastOrNull()?.undo()
    }
}

fun main() {
    val doc = Document()
    val history = History()
    history.run(AppendText(doc, "Hello"))
    history.run(AppendText(doc, ", world"))
    println(doc.text)
    history.run(Clear(doc))
    println("[" + doc.text + "]")
    history.undo()
    println(doc.text)
    history.undo()
    println(doc.text)
    // If no undo is needed, a plain `() -> Unit` lambda is the command.
}
