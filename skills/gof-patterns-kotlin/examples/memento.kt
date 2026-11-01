// Memento: an immutable data class is the snapshot, and the editor restores from it.

class Editor {
    var text: String = ""
    var cursor: Int = 0

    // The memento holds only values, so the caller cannot change editor internals through it.
    data class Snapshot(val text: String, val cursor: Int)

    fun save() = Snapshot(text, cursor)

    fun restore(snapshot: Snapshot) {
        text = snapshot.text
        cursor = snapshot.cursor
    }

    fun type(chars: String) {
        text = text.substring(0, cursor) + chars + text.substring(cursor)
        cursor += chars.length
    }
}

fun main() {
    val editor = Editor()
    val undoStack = ArrayDeque<Editor.Snapshot>()

    undoStack.addLast(editor.save()); editor.type("Hello")
    undoStack.addLast(editor.save()); editor.type(" world")
    println(editor.text)

    editor.restore(undoStack.removeLast())
    println(editor.text)
    editor.restore(undoStack.removeLast())
    println("[" + editor.text + "] cursor=" + editor.cursor)
}
