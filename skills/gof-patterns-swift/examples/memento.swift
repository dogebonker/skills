// Memento: because the editor is a struct, a snapshot is just a copy; the history stores them.
struct TextEditor {
    private(set) var text = ""
    private(set) var cursor = 0

    mutating func type(_ added: String) {
        text += added
        cursor = text.count
    }

    // The memento is opaque to callers: only the editor can read its fields.
    struct Snapshot {
        fileprivate let text: String
        fileprivate let cursor: Int
    }

    func snapshot() -> Snapshot { Snapshot(text: text, cursor: cursor) }

    mutating func restore(_ snapshot: Snapshot) {
        text = snapshot.text
        cursor = snapshot.cursor
    }
}

var editor = TextEditor()
var undoStack: [TextEditor.Snapshot] = []

editor.type("Hello")
undoStack.append(editor.snapshot())
editor.type(", world")
undoStack.append(editor.snapshot())
editor.type("!!!")
print(editor.text)

editor.restore(undoStack.removeLast())
print(editor.text)
editor.restore(undoStack.removeLast())
print(editor.text, editor.cursor)
