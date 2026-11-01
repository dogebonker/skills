from dataclasses import dataclass

from tariffs import FlatTariff, Tariff

VAT_RATE = 0.06
DEMAND_CHARGE_PER_KW = 9.5
ESTIMATE_HOLDBACK = 0.1
USAGE_ALERT_CHANGE = 0.4
INSTALMENT_THRESHOLD = 250.0
INSTALMENT_COUNT = 3
GRID_CO2_KG_PER_KWH = 0.19


@dataclass
class Reading:
    meter_id: str
    kwh: float
    read_type: str


@dataclass
class Account:
    account_id: str
    name: str
    country: str
    credit: float
    previous_kwh: float


class DemandTariff(Tariff):
    def __init__(self, rate: float, peak_kw: float) -> None:
        self.rate = rate
        self.peak_kw = peak_kw

    def charge(self, kwh: float) -> float:
        return kwh * self.rate + self.peak_kw * DEMAND_CHARGE_PER_KW


def normalize_payload(payload: object) -> list[Reading]:
    if not isinstance(payload, dict) or not isinstance(payload.get("reads"), list):
        raise ValueError("unexpected meter payload")
    readings = []
    for item in payload["reads"]:
        if isinstance(item, dict) and isinstance(item.get("kwh"), (int, float)):
            readings.append(Reading(str(item.get("meter", "")), float(item["kwh"]), str(item.get("type", "actual"))))
    return readings


def round_kwh(kwh: float) -> float:
    return round(kwh, 3)


def _interpolate(start: Reading, end: Reading, steps: int) -> list[float]:
    step = (end.kwh - start.kwh) / steps
    return [start.kwh + step * i for i in range(1, steps)]


def backfill_gaps(readings: list[Reading]) -> list[float]:
    return [v for a, b in zip(readings, readings[1:]) for v in _interpolate(a, b, 4)]


def smooth_spikes(readings: list[Reading]) -> list[float]:
    return [sum(_interpolate(a, b, 2)) / 2 for a, b in zip(readings, readings[1:])]


def is_estimated(reading: Reading) -> bool:
    return reading.read_type.strip().lower() == "estimated"


def close_billing_cycle(account: Account, readings: list[Reading], tariff: Tariff) -> dict:
    warnings = []
    usable = []
    for reading in readings:
        if not reading.meter_id:
            warnings.append("reading without meter id skipped")
            continue
        if reading.kwh < 0:
            warnings.append(f"negative read on {reading.meter_id} skipped")
            continue
        usable.append(reading)
    if not usable:
        raise ValueError(f"no usable reads for account {account.account_id}")
    estimated_count = sum(1 for reading in usable if is_estimated(reading))
    if estimated_count:
        warnings.append(f"{estimated_count} estimated reads this cycle")

    per_meter: dict[str, float] = {}
    for reading in usable:
        per_meter[reading.meter_id] = per_meter.get(reading.meter_id, 0.0) + reading.kwh
    total_kwh = sum(per_meter.values())
    peak_meter = max(per_meter, key=lambda meter_id: per_meter[meter_id])
    if account.previous_kwh:
        change = (total_kwh - account.previous_kwh) / account.previous_kwh
        if abs(change) >= USAGE_ALERT_CHANGE:
            warnings.append(f"usage changed {change:+.0%} against last cycle")

    energy_charge = tariff.charge(total_kwh)
    estimated_kwh = 0.0
    for reading in usable:
        if reading.read_type == "estimated":
            estimated_kwh += reading.kwh
    held_back = energy_charge * estimated_kwh / total_kwh * ESTIMATE_HOLDBACK if total_kwh else 0.0
    net = energy_charge - held_back
    credit_used = min(account.credit, net)
    net -= credit_used
    vat = round(net * VAT_RATE, 2)
    amount_due = round(net + vat, 2)
    carbon_kg = round(total_kwh * GRID_CO2_KG_PER_KWH, 1)

    instalments = []
    if amount_due > INSTALMENT_THRESHOLD:
        part = round(amount_due / INSTALMENT_COUNT, 2)
        instalments = [part] * (INSTALMENT_COUNT - 1)
        instalments.append(round(amount_due - sum(instalments), 2))
        warnings.append(f"amount due split into {INSTALMENT_COUNT} instalments")

    country = country_alpha3().get(account.country, account.country)
    lines = [f"Statement for {account.name} ({account.account_id}, {country})"]
    for meter_id in sorted(per_meter):
        share = per_meter[meter_id] / total_kwh if total_kwh else 0.0
        lines.append(f"  {meter_id}: {per_meter[meter_id]:.3f} kWh ({share:.0%})")
    lines.append(f"Energy {energy_charge:.2f}")
    if held_back:
        lines.append(f"Held back for estimated reads -{held_back:.2f}")
    if credit_used:
        lines.append(f"Account credit -{credit_used:.2f}")
    lines.append(f"VAT {vat:.2f}")
    lines.append(f"Amount due {amount_due:.2f}")
    for number, instalment in enumerate(instalments, 1):
        lines.append(f"  Instalment {number}: {instalment:.2f}")
    lines.append(f"Meters read: {len(per_meter)}, estimated reads: {estimated_count}")
    lines.append(f"Estimated emissions {carbon_kg} kg CO2")
    lines.extend(f"Note: {warning}" for warning in warnings)

    export_row = {
        "account": account.account_id,
        "country": country,
        "kwh": total_kwh,
        "peak_meter": peak_meter,
        "estimated_kwh": estimated_kwh,
        "credit_used": round(credit_used, 2),
        "vat": vat,
        "amount_due": amount_due,
        "instalments": len(instalments),
        "carbon_kg": carbon_kg,
    }
    return {
        "lines": lines,
        "export": export_row,
        "instalments": instalments,
        "credit_left": round(account.credit - credit_used, 2),
    }


def country_alpha3() -> dict[str, str]:
    return {
        "AD": "AND",
        "AE": "ARE",
        "AO": "AGO",
        "AR": "ARG",
        "AT": "AUT",
        "AU": "AUS",
        "BE": "BEL",
        "BG": "BGR",
        "BO": "BOL",
        "BR": "BRA",
        "CA": "CAN",
        "CH": "CHE",
        "CL": "CHL",
        "CN": "CHN",
        "CO": "COL",
        "CV": "CPV",
        "CY": "CYP",
        "CZ": "CZE",
        "DE": "DEU",
        "DK": "DNK",
        "DZ": "DZA",
        "EC": "ECU",
        "EE": "EST",
        "EG": "EGY",
        "ES": "ESP",
        "FI": "FIN",
        "FR": "FRA",
        "GB": "GBR",
        "GR": "GRC",
        "GW": "GNB",
        "HK": "HKG",
        "HR": "HRV",
        "HU": "HUN",
        "ID": "IDN",
        "IE": "IRL",
        "IL": "ISR",
        "IN": "IND",
        "IS": "ISL",
        "IT": "ITA",
        "JP": "JPN",
        "KE": "KEN",
        "KR": "KOR",
        "LT": "LTU",
        "LU": "LUX",
        "LV": "LVA",
        "MA": "MAR",
        "MT": "MLT",
        "MX": "MEX",
        "MY": "MYS",
        "MZ": "MOZ",
        "NG": "NGA",
        "NL": "NLD",
        "NO": "NOR",
        "NZ": "NZL",
        "PE": "PER",
        "PH": "PHL",
        "PK": "PAK",
        "PL": "POL",
        "PT": "PRT",
        "PY": "PRY",
        "QA": "QAT",
        "RO": "ROU",
        "RS": "SRB",
        "SA": "SAU",
        "SE": "SWE",
        "SG": "SGP",
        "SI": "SVN",
        "SK": "SVK",
        "ST": "STP",
        "TH": "THA",
        "TL": "TLS",
        "TN": "TUN",
        "TR": "TUR",
        "TW": "TWN",
        "UA": "UKR",
        "US": "USA",
        "UY": "URY",
        "VN": "VNM",
        "ZA": "ZAF",
    }


if __name__ == "__main__":
    payload = {"reads": [{"meter": "M-1", "kwh": 210.5, "type": "actual"}, {"meter": "M-2", "kwh": 95.25, "type": " Estimated"}, {"meter": "M-1", "kwh": 40, "type": "estimated"}]}
    account = Account("AC-9", "Rua Nova Bakery", "PT", 12.0, 300.0)
    result = close_billing_cycle(account, normalize_payload(payload), FlatTariff(0.21))
    print("\n".join(result["lines"]), result["export"], DemandTariff(0.18, 12.0).charge(100.0))
