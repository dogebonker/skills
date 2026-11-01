// Chain of Responsibility: each handler either answers the request or passes it on.
struct Ticket {
    let subject: String
    let severity: Int
}

protocol SupportHandler {
    func handle(_ ticket: Ticket) -> String?
}

struct Level1Support: SupportHandler {
    func handle(_ ticket: Ticket) -> String? {
        ticket.severity <= 1 ? "L1 resolved '\(ticket.subject)'" : nil
    }
}

struct Level2Support: SupportHandler {
    func handle(_ ticket: Ticket) -> String? {
        ticket.severity <= 3 ? "L2 resolved '\(ticket.subject)'" : nil
    }
}

struct OnCallEngineer: SupportHandler {
    func handle(_ ticket: Ticket) -> String? { "paged engineer for '\(ticket.subject)'" }
}

// The chain is just an ordered array; the first non-nil answer wins.
func route(_ ticket: Ticket, through chain: [any SupportHandler]) -> String {
    for handler in chain {
        if let answer = handler.handle(ticket) { return answer }
    }
    return "unhandled"
}

let chain: [any SupportHandler] = [Level1Support(), Level2Support(), OnCallEngineer()]
for ticket in [Ticket(subject: "password reset", severity: 1),
               Ticket(subject: "slow reports", severity: 3),
               Ticket(subject: "database down", severity: 5)] {
    print(route(ticket, through: chain))
}
