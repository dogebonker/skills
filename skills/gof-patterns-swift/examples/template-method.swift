// Template Method: a protocol extension fixes the algorithm; conformers fill in the steps.
protocol ReportGenerator {
    func fetchRows() -> [String]
    func format(_ rows: [String]) -> String
    var wantsFooter: Bool { get } // optional hook with a default
}

extension ReportGenerator {
    var wantsFooter: Bool { false }

    // The template method: not a requirement, so it is statically dispatched; do not redeclare it in conformers.
    func generate() -> String {
        let rows = fetchRows()
        var output = format(rows)
        if wantsFooter { output += "\n-- \(rows.count) rows --" }
        return output
    }
}

struct SalesReport: ReportGenerator {
    func fetchRows() -> [String] { ["north: 10", "south: 7"] }
    func format(_ rows: [String]) -> String { rows.joined(separator: "\n") }
    var wantsFooter: Bool { true }
}

struct CSVReport: ReportGenerator {
    func fetchRows() -> [String] { ["a", "b", "c"] }
    func format(_ rows: [String]) -> String { rows.joined(separator: ",") }
}

print(SalesReport().generate())
print(CSVReport().generate())
