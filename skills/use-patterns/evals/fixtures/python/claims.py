from datetime import date

import policies
from policies import CarPolicy, HomePolicy, TravelPolicy, claim_limit, describe, premium, tax_rate

class AuditLog:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.entries = []
        return cls._instance

    def record(self, text: str) -> None:
        self.entries.append(text)

class Adjuster:
    def __init__(self, name: str) -> None:
        self.name = name
        self.inbox: list[str] = []
    def send(self, message: str) -> None:
        self.inbox.append(message)

class Claim:
    def __init__(self, policy, amount, incident_date, description, photos, police_report, witness, adjuster, region):
        self.policy = policy
        self.amount = amount
        self.incident_date = incident_date
        self.description = description
        self.photos = photos
        self.police_report = police_report
        self.witness = witness
        self.adjuster = adjuster
        self.region = region
        self.status = "open"

def notify_adjuster(claim: Claim, message: str) -> None:
    if claim.adjuster is not None:
        claim.adjuster.send(message)
    else:
        AuditLog().record(f"unassigned: {message}")

def adjuster_name(claim: Claim) -> str:
    return claim.adjuster.name if claim.adjuster is not None else "Unassigned"

def pending_messages(claim: Claim) -> int:
    return len(claim.adjuster.inbox) if claim.adjuster is not None else 0

def format_amount(amount: float, with_symbol: bool) -> str:
    return f"EUR {amount:,.2f}" if with_symbol else f"{amount:.2f}"

class CarAssessor:
    def estimate(self, claim: Claim) -> float:
        return claim.amount * (0.9 if claim.police_report else 0.7)

class HomeAssessor:
    def estimate(self, claim: Claim) -> float:
        return claim.amount * (1 + tax_rate(claim.region)) if claim.photos else claim.amount * 0.5

class TravelAssessor:
    def estimate(self, claim: Claim) -> float:
        return min(claim.amount, 1500.0) if claim.witness else claim.amount * 0.4

class CarClaimProcessor:
    def process(self, claim: Claim) -> float:
        estimate = CarAssessor().estimate(claim)
        claim.status = "approved" if estimate <= claim_limit(claim.policy) else "referred"
        notify_adjuster(claim, f"{claim.status}: {describe(claim.policy)}")
        AuditLog().record(f"{adjuster_name(claim)} {format_amount(estimate, True)}")
        return estimate

class HomeClaimProcessor:
    def process(self, claim: Claim) -> float:
        estimate = HomeAssessor().estimate(claim)
        claim.status = "approved" if estimate <= claim_limit(claim.policy) else "referred"
        notify_adjuster(claim, f"{claim.status}: {describe(claim.policy)}")
        AuditLog().record(f"{adjuster_name(claim)} {format_amount(estimate, True)}")
        return estimate

class TravelClaimProcessor:
    def process(self, claim: Claim) -> float:
        estimate = TravelAssessor().estimate(claim)
        claim.status = "approved" if estimate <= claim_limit(claim.policy) else "referred"
        notify_adjuster(claim, f"{claim.status}: {describe(claim.policy)}")
        AuditLog().record(f"{adjuster_name(claim)} {format_amount(estimate, True)}")
        return estimate

if __name__ == "__main__":
    car = CarPolicy("Rui", 18000, 23)
    home = HomePolicy("Marta", 240000, True)
    a = Claim(car, 3200, "2026-09-12", "rear bumper", None, "PR-881", None, Adjuster("Ines"), "north")
    b = Claim(home, 12000, "2026-10-02", "kitchen flood", ["p1.jpg"], None, "neighbour", None, "islands")
    print(CarClaimProcessor().process(a), a.status, a.adjuster.inbox)
    print(HomeClaimProcessor().process(b), b.status, adjuster_name(b))
    t = Claim(TravelPolicy("Joao", 9, "Peru"), 900, "2026-10-20", "lost luggage", None, None, "guide", Adjuster("Ines"), "south")
    print(TravelClaimProcessor().process(t), pending_messages(t), pending_messages(b), AuditLog().entries)
    print(premium(car), premium(home), format_amount(premium(home), False))
    print(policies.parse_claim_form({"amount": "900"}), policies.ClaimRecord("Rui", 900).amount, policies.payout(3200, 250, True, False, 2500))
    period = policies.Period(date(2026, 1, 1), date(2026, 3, 31))
    print(policies.ClaimReminder().remind("rui@example.com", date(2026, 9, 1)), period.days(), period.intersect(policies.Period(date(2026, 3, 1), date(2026, 4, 1))))
    print(policies.notify_holder([policies.EmailNotifier(), policies.SmsNotifier()], "rui@example.com", "Claim received"), policies.MAX_PHOTOS_PER_CLAIM, policies.REVIEW_SLA_DAYS)
