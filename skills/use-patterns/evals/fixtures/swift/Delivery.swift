struct Dish {
    let name: String
    let price: Double
    let category: String
}

struct Combo {
    let name: String
    let discount: Double
    let parts: [Any]
}

func price(of node: Any) -> Double {
    if let dish = node as? Dish { return dish.price }
    if let combo = node as? Combo { return combo.parts.map(price(of:)).reduce(0, +) * (1 - combo.discount) }
    return 0
}

func names(in node: Any) -> [String] {
    if let dish = node as? Dish { return [dish.name] }
    if let combo = node as? Combo { return combo.parts.flatMap(names(in:)) }
    return []
}

func prepMinutes(category: String) -> Int {
    switch category {
    case "drinks": return 2
    case "starters": return 8
    case "mains": return 15
    default: return 10
    }
}

struct Delivery {
    let feeMode: String
    let km: Double
    let basketTotal: Double
}

func deliveryFee(_ d: Delivery) -> Double {
    switch d.feeMode {
    case "distance": return 1.5 + d.km * 0.6
    case "flat": return 2.99
    case "freeOver": return d.basketTotal >= 25 ? 0 : 3.49
    case "peak": return (1.5 + d.km * 0.6) * 1.5
    default: preconditionFailure("unknown fee mode \(d.feeMode)")
    }
}

func feeExplanation(_ d: Delivery) -> String {
    switch d.feeMode {
    case "distance": return "Based on \(d.km) km"
    case "flat": return "Flat fee"
    case "freeOver": return d.basketTotal >= 25 ? "Free delivery" : "Free over 25"
    case "peak": return "Busy hours surcharge"
    default: preconditionFailure("unknown fee mode \(d.feeMode)")
    }
}

struct PriceCalculator {
    var addServiceFee = false
    var addVat = false
    var roundUpForCharity = false

    func total(subtotal: Double) -> Double {
        var amount = subtotal
        if addServiceFee { amount += max(0.5, amount * 0.05) }
        if addVat { amount *= 1.23 }
        if roundUpForCharity { amount = amount.rounded(.up) }
        return amount
    }
}

protocol Courier { func eta(km: Double) -> Int }
struct BikeCourier: Courier { func eta(km: Double) -> Int { Int(km * 4) } }
struct CarCourier: Courier { func eta(km: Double) -> Int { Int(km * 2) + 5 } }

enum Vehicle { case bike, car }

func makeCourier(_ vehicle: Vehicle) -> any Courier {
    switch vehicle {
    case .bike: return BikeCourier()
    case .car: return CarCourier()
    }
}

struct Order {
    let id: String
    let items: [Any]
}

enum OrderFactory {
    static func makeOrder(id: String, items: [Any]) -> Order {
        Order(id: id, items: items)
    }
}

final class StatusBanner { var text = ""; func show(_ s: String) { text = "Order is \(s)" } }
final class EtaClock { var minutes = 0; func recalculate(for s: String) { minutes = s == "on the way" ? 12 : 0 } }
final class ReceiptLog { var events: [String] = []; func append(_ s: String) { events.append(s) } }

final class OrderTracker {
    let banner = StatusBanner()
    let eta = EtaClock()
    let receipts = ReceiptLog()
    var status = "placed" {
        didSet {
            banner.show(status)
            eta.recalculate(for: status)
            receipts.append(status)
        }
    }
}

let burger = Dish(name: "Burger", price: 9.5, category: "mains")
let menu = Combo(name: "Lunch", discount: 0.1, parts: [burger, Dish(name: "Cola", price: 2.5, category: "drinks"), Combo(name: "Sides", discount: 0, parts: [Dish(name: "Fries", price: 3, category: "starters")])])
let order = OrderFactory.makeOrder(id: "D-42", items: [menu])
let delivery = Delivery(feeMode: "freeOver", km: 3.2, basketTotal: price(of: menu))
let calculator = PriceCalculator(addServiceFee: true, addVat: true, roundUpForCharity: false)
print(order.id, names(in: menu), price(of: menu), prepMinutes(category: burger.category))
print(deliveryFee(delivery), feeExplanation(delivery), calculator.total(subtotal: price(of: menu)))
print(makeCourier(.bike).eta(km: delivery.km))
let tracker = OrderTracker()
tracker.status = "on the way"
print(tracker.banner.text, tracker.eta.minutes, tracker.receipts.events)

func canDeliver(to d: Delivery) -> Bool { d.km <= 8 }

func zoneLabel(for d: Delivery) -> String { d.km > 8 ? "Outside delivery zone" : "Inside delivery zone" }

func courierBonus(km: Double) -> Double { km > 8.0 ? 1.5 : 0 }

let maxDishesPerCombo = 6
let courierShiftHours = 6

protocol MenuStore {
    func dishes() -> [Dish]
    func add(_ dish: Dish)
    func remove(named name: String)
    func importCSV(_ text: String)
    func exportCSV() -> String
}

final class EditableMenu: MenuStore {
    private var items: [Dish] = []
    func dishes() -> [Dish] { items }
    func add(_ dish: Dish) { items.append(dish) }
    func remove(named name: String) { items.removeAll { $0.name == name } }
    func importCSV(_ text: String) {
        for line in text.split(separator: "\n") {
            let f = line.split(separator: ",")
            add(Dish(name: String(f[0]), price: Double(f[1]) ?? 0, category: String(f[2])))
        }
    }
    func exportCSV() -> String { items.map { "\($0.name),\($0.price),\($0.category)" }.joined(separator: "\n") }
}

final class PublishedMenu: MenuStore {
    private let items: [Dish]
    init(items: [Dish]) { self.items = items }
    func dishes() -> [Dish] { items }
    func add(_ dish: Dish) { fatalError("published menus are read-only") }
    func remove(named name: String) { fatalError("published menus are read-only") }
    func importCSV(_ text: String) { fatalError("published menus are read-only") }
    func exportCSV() -> String { items.map(\.name).joined(separator: ",") }
}

func cheapestDish(in store: any MenuStore) -> Dish? { store.dishes().min { $0.price < $1.price } }

final class FeeCache {
    private var cache: [String: Double] = [:]
    func fee(_ d: Delivery) -> Double {
        let key = "\(d.feeMode)-\(Int(d.km))"
        if let hit = cache[key] { return hit }
        let value = deliveryFee(d)
        cache[key] = value
        return value
    }
}

struct Basket {
    private(set) var dishes: [Dish] = []
    var count: Int { dishes.count }
    var isEmpty: Bool { dishes.isEmpty }
    var total: Double { dishes.reduce(0) { $0 + $1.price } }
    mutating func add(_ dish: Dish) { dishes.append(dish) }
    mutating func remove(named name: String) { dishes.removeAll { $0.name == name } }
    func contains(named name: String) -> Bool { dishes.contains { $0.name == name } }
    func cheapest() -> Dish? { dishes.min { $0.price < $1.price } }
    func byCategory() -> [String: [Dish]] { Dictionary(grouping: dishes, by: \.category) }
}

let editable = EditableMenu()
editable.importCSV("Soup,4.5,starters\nTea,1.8,drinks")
let published = PublishedMenu(items: editable.dishes())
var basket = Basket()
basket.add(burger)
editable.dishes().forEach { basket.add($0) }
basket.remove(named: "Tea")
print(canDeliver(to: delivery), zoneLabel(for: delivery), courierBonus(km: 9), maxDishesPerCombo, courierShiftHours)
print(cheapestDish(in: published)?.name ?? "-", editable.exportCSV().count, FeeCache().fee(delivery))
print(basket.count, basket.isEmpty, basket.total, basket.contains(named: "Soup"), basket.cheapest()?.name ?? "-", basket.byCategory().keys.sorted())
