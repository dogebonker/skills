// SRP in Swift: split by reason to change into separate types. Extensions
// organise one type's code; they do not separate responsibilities.

struct LineItem {
    let name: String
    let cents: Int
}

// --- Violation: one class computes totals (finance), formats text (design)
// and archives receipts (platform). Any of the three changes edits it.
final class ReceiptManagerV1 {
    private(set) var archive: [String: String] = [:]

    func process(id: String, items: [LineItem]) -> String {
        let subtotal = items.reduce(0) { $0 + $1.cents }
        let tax = subtotal * 23 / 100
        var text = items.map { "\($0.name): \(money($0.cents))" }.joined(separator: "\n")
        text += "\nTotal: \(money(subtotal + tax))"
        archive[id] = text
        return text
    }

    private func money(_ cents: Int) -> String {
        let rest = cents % 100
        return "€\(cents / 100)." + (rest < 10 ? "0" : "") + "\(rest)"
    }
}

// --- Fix: three small value types, each with one reason to change.
struct ReceiptCalculator {
    let taxPercent: Int
    func total(_ items: [LineItem]) -> Int {
        let subtotal = items.reduce(0) { $0 + $1.cents }
        return subtotal + subtotal * taxPercent / 100
    }
}

struct ReceiptFormatter {
    func money(_ cents: Int) -> String {
        let rest = cents % 100
        return "€\(cents / 100)." + (rest < 10 ? "0" : "") + "\(rest)"
    }
    func text(_ items: [LineItem], total: Int) -> String {
        items.map { "\($0.name): \(money($0.cents))" }.joined(separator: "\n")
            + "\nTotal: \(money(total))"
    }
}

struct ReceiptArchive {
    private(set) var stored: [String: String] = [:]
    mutating func save(_ text: String, id: String) { stored[id] = text }
}

let items = [LineItem(name: "Espresso", cents: 250), LineItem(name: "Croissant", cents: 305)]

let before = ReceiptManagerV1().process(id: "r-1", items: items)

let calculator = ReceiptCalculator(taxPercent: 23)
let formatter = ReceiptFormatter()
var archive = ReceiptArchive()
let after = formatter.text(items, total: calculator.total(items))
archive.save(after, id: "r-1")

print(after)
print("same output: \(before == after && archive.stored["r-1"] == after)")
