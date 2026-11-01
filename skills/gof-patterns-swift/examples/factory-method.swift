// Factory Method: each exporter type decides which Document it produces.
protocol Document {
    func render() -> String
}

struct PDFDocument: Document {
    let title: String
    func render() -> String { "%PDF-1.7 \(title)" }
}

struct HTMLDocument: Document {
    let title: String
    func render() -> String { "<h1>\(title)</h1>" }
}

protocol Exporter {
    // The factory method.
    func makeDocument(title: String) -> any Document
}

extension Exporter {
    // Shared logic that depends on the product, not on its concrete type.
    func export(title: String) -> String {
        let document = makeDocument(title: title)
        return "exported: " + document.render()
    }
}

struct PDFExporter: Exporter {
    func makeDocument(title: String) -> any Document { PDFDocument(title: title) }
}

struct HTMLExporter: Exporter {
    func makeDocument(title: String) -> any Document { HTMLDocument(title: title) }
}

let exporters: [any Exporter] = [PDFExporter(), HTMLExporter()]
for exporter in exporters {
    print(exporter.export(title: "Invoice 42"))
}
