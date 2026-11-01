protocol Tariff {
    func charge(minutes: Int) -> Double
}

struct HourlyTariff: Tariff {
    let perHour: Double
    let dailyCap: Double

    func charge(minutes: Int) -> Double {
        let hours = (minutes + 59) / 60
        return min(Double(hours) * perHour, dailyCap)
    }
}

private func formatDuration(minutes: Int) -> String {
    guard minutes >= 0 else { return "0m" }
    return minutes >= 60 ? "\(minutes / 60)h \(minutes % 60)m" : "\(minutes)m"
}

func euros(_ amount: Double) -> String {
    String(format: "%.2f EUR", amount)
}

func receiptLine(plate: String, minutes: Int, amount: Double) -> String {
    "\(plate) parked \(formatDuration(minutes: minutes)): \(euros(amount))"
}
