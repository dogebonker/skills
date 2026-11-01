// Decorator: wrap a protocol value and add behavior while keeping the same interface.
protocol DataSource {
    func read() -> String
}

struct FileSource: DataSource {
    let content: String
    func read() -> String { content }
}

struct UppercasedSource<Base: DataSource>: DataSource {
    let base: Base
    func read() -> String { base.read().uppercased() }
}

struct LoggedSource<Base: DataSource>: DataSource {
    let base: Base
    func read() -> String {
        let result = base.read()
        print("read \(result.count) characters")
        return result
    }
}

// Fluent wrapping helpers via a protocol extension.
extension DataSource {
    func uppercased() -> UppercasedSource<Self> { UppercasedSource(base: self) }
    func logged() -> LoggedSource<Self> { LoggedSource(base: self) }
}

let source = FileSource(content: "hello decorators").uppercased().logged()
print(source.read())
