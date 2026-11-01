// Composite: files and folders share one interface; an indirect enum models the tree.
indirect enum FileNode {
    case file(name: String, bytes: Int)
    case folder(name: String, children: [FileNode])

    var totalBytes: Int {
        switch self {
        case .file(_, let bytes):
            return bytes
        case .folder(_, let children):
            return children.reduce(0) { $0 + $1.totalBytes }
        }
    }

    func outline(depth: Int = 0) -> [String] {
        let pad = String(repeating: "  ", count: depth)
        switch self {
        case .file(let name, let bytes):
            return ["\(pad)\(name) (\(bytes))"]
        case .folder(let name, let children):
            return ["\(pad)\(name)/"] + children.flatMap { $0.outline(depth: depth + 1) }
        }
    }
}

let tree = FileNode.folder(name: "project", children: [
    .file(name: "main.swift", bytes: 1200),
    .folder(name: "assets", children: [
        .file(name: "logo.png", bytes: 5000),
        .file(name: "icon.png", bytes: 800),
    ]),
])
print(tree.outline().joined(separator: "\n"))
print("total:", tree.totalBytes)
