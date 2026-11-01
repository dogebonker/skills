import Foundation

struct ParkingSession {
    let plate: String
    let region: String
    let vehicleType: String
    let minutes: Int
}

struct Payment {
    let plate: String
    let amount: Double
}

struct ShiftReport {
    let lines: [String]
    let warnings: [String]
    let takings: Double
}

let motorcycleShare = 0.5
let longStayMinutes = 24 * 60
let lostTicketFee = 25.0
let paymentTolerance = 0.005
let legacyHourlyRates: [String: Double] = ["A": 2.4, "B": 1.8, "C": 1.2]

struct EventDayTariff: Tariff {
    let flatFee: Double

    func charge(minutes: Int) -> Double { flatFee }
}

func parsePayload(_ data: Data) -> ParkingSession? {
    guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let plate = json["plate"] as? String else { return nil }
    let region = json["region"] as? String ?? ""
    let vehicle = json["vehicle"] as? [String: Any]
    let minutes = (json["duration_s"] as? Double).map { Int($0 / 60) } ?? 0
    return ParkingSession(plate: plate, region: region, vehicleType: vehicle?["class"] as? String ?? "car", minutes: minutes)
}

private func formatDuration(minutes: Int) -> String {
    minutes >= 60 ? "\(minutes / 60)h \(minutes % 60)m" : "\(minutes)m"
}

func nightsParked(_ session: ParkingSession) -> Int {
    session.minutes / longStayMinutes
}

func overnightSurcharge(_ sessions: [ParkingSession], perNight: Double) -> Double {
    sessions.reduce(0) { $0 + Double(nightsParked($1)) * perNight }
}

func monthlyPassBreakEven(_ session: ParkingSession, passPrice: Double, perNight: Double) -> Int {
    Int(passPrice / (Double(max(nightsParked(session), 1)) * perNight))
}

func legacyRate(for zone: String) -> Double {
    legacyHourlyRates[zone] ?? 2.0
}

func isMotorcycle(_ session: ParkingSession) -> Bool {
    session.vehicleType.trimmingCharacters(in: .whitespaces).lowercased() == "motorcycle"
}

func closeShift(sessions: [ParkingSession], payments: [Payment], tariff: any Tariff) -> ShiftReport {
    var warnings: [String] = []
    var valid: [ParkingSession] = []
    for session in sessions {
        guard !session.plate.isEmpty else {
            warnings.append("session without a plate skipped")
            continue
        }
        guard session.minutes > 0 else {
            warnings.append("\(session.plate): zero-length session skipped")
            continue
        }
        valid.append(session)
    }
    let motorcycles = valid.filter(isMotorcycle).count

    var expected: [String: Double] = [:]
    for session in valid {
        var amount = tariff.charge(minutes: session.minutes)
        if session.vehicleType == "motorcycle" {
            amount *= motorcycleShare
        }
        if session.minutes >= longStayMinutes {
            warnings.append("\(session.plate) stayed over a day")
        }
        expected[session.plate, default: 0] += amount
    }

    var paid: [String: Double] = [:]
    for payment in payments {
        paid[payment.plate, default: 0] += payment.amount
    }
    var shortfalls: [String] = []
    var refunds: [String] = []
    var lostTickets = 0
    for (plate, amount) in expected.sorted(by: { $0.key < $1.key }) {
        let received = paid[plate] ?? 0
        if received == 0 {
            lostTickets += 1
            shortfalls.append("\(plate): unpaid, lost-ticket fee \(lostTicketFee)")
        } else if received + paymentTolerance < amount {
            shortfalls.append("\(plate): short by \(euros(amount - received))")
        } else if received > amount + paymentTolerance {
            refunds.append("\(plate): refund \(euros(received - amount))")
        }
    }
    let takings = paid.values.reduce(0, +)
    let expectedTotal = expected.values.reduce(0, +) + Double(lostTickets) * lostTicketFee

    let names = plateJurisdictions()
    var byRegion: [String: Int] = [:]
    for session in valid {
        byRegion[names[session.region] ?? "Unknown", default: 0] += 1
    }
    let topRegions = byRegion.sorted { $0.value > $1.value || ($0.value == $1.value && $0.key < $1.key) }
        .prefix(3)
        .map { "\($0.key) \($0.value)" }

    var lines = ["Shift close: \(valid.count) sessions, \(motorcycles) motorcycles"]
    for session in valid.sorted(by: { $0.minutes > $1.minutes }).prefix(3) {
        lines.append(receiptLine(plate: session.plate, minutes: session.minutes, amount: expected[session.plate] ?? 0))
    }
    lines.append("Expected \(euros(expectedTotal)), taken \(euros(takings))")
    lines.append("Visitors by region: \(topRegions.joined(separator: ", "))")
    lines.append(contentsOf: shortfalls)
    lines.append(contentsOf: refunds)
    if lostTickets > 0 {
        lines.append("Lost tickets: \(lostTickets)")
    }
    let averageMinutes = valid.map(\.minutes).reduce(0, +) / max(valid.count, 1)
    lines.append("Average stay \(averageMinutes) minutes")

    var export = ["plate,region,minutes,expected,paid"]
    for session in valid {
        let due = expected[session.plate] ?? 0
        let received = paid[session.plate] ?? 0
        export.append("\(session.plate),\(session.region),\(session.minutes),\(due),\(received)")
    }
    lines.append("Export rows: \(export.count - 1)")
    warnings.append(contentsOf: export.dropFirst().filter { $0.hasSuffix(",0.0") }.map { "unpaid row \($0)" })
    return ShiftReport(lines: lines, warnings: warnings, takings: takings)
}

func plateJurisdictions() -> [String: String] {
    [
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
        "DC": "District of Columbia",
        "PR": "Puerto Rico",
        "GU": "Guam",
        "VI": "U.S. Virgin Islands",
        "AS": "American Samoa",
        "MP": "Northern Mariana Islands",
        "AB": "Alberta",
        "BC": "British Columbia",
        "MB": "Manitoba",
        "NB": "New Brunswick",
        "NL": "Newfoundland and Labrador",
        "NS": "Nova Scotia",
        "NT": "Northwest Territories",
        "NU": "Nunavut",
        "ON": "Ontario",
        "PE": "Prince Edward Island",
        "QC": "Quebec",
        "SK": "Saskatchewan",
        "YT": "Yukon",
        "AGU": "Aguascalientes",
        "BCN": "Baja California",
        "CHH": "Chihuahua",
        "COA": "Coahuila",
        "JAL": "Jalisco",
        "NLE": "Nuevo Leon",
        "SON": "Sonora",
        "TAM": "Tamaulipas",
        "CMX": "Mexico City",
        "YUC": "Yucatan",
    ]
}

@main
enum GarageApp {
    static func main() {
        let feed = [
            #"{"plate": "7ABC123", "region": "CA", "vehicle": {"class": "car"}, "duration_s": 9000}"#,
            #"{"plate": "M0TO77", "region": "TX", "vehicle": {"class": "Motorcycle"}, "duration_s": 5400}"#,
            #"{"plate": "BIKE9", "region": "ON", "vehicle": {"class": "motorcycle"}, "duration_s": 3600}"#,
        ]
        let sessions = feed.compactMap { parsePayload(Data($0.utf8)) }
        let payments = [Payment(plate: "7ABC123", amount: 9.0), Payment(plate: "M0TO77", amount: 3.0), Payment(plate: "BIKE9", amount: 2.0)]
        let report = closeShift(sessions: sessions, payments: payments, tariff: HourlyTariff(perHour: 3.0, dailyCap: 30))
        print((report.lines + report.warnings).joined(separator: "\n"), EventDayTariff(flatFee: 15).charge(minutes: 300))
    }
}
