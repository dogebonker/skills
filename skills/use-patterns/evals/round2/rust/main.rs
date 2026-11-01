use std::any::Any;
use std::collections::HashMap;

pub mod payslip;

use payslip::{money, Deduction, PensionContribution};

pub const STANDARD_WEEK_HOURS: f64 = 40.0;
pub const OVERTIME_MULTIPLIER: f64 = 1.5;
pub const INCOME_TAX_RATE: f64 = 0.21;
pub const SOCIAL_SECURITY_RATE: f64 = 0.11;
pub const LEGACY_TAX_BANDS: [(f64, f64); 3] = [(0.0, 0.145), (7_500.0, 0.21), (20_000.0, 0.285)];

pub struct Employee {
    pub id: String,
    pub name: String,
    pub country: String,
    pub contract: String,
    pub rate: f64,
}

pub struct ClockEvent {
    pub employee_id: String,
    pub hours: f64,
}

pub struct UnionDues {
    pub monthly: f64,
}

impl Deduction for UnionDues {
    fn label(&self) -> String {
        String::from("Union dues")
    }

    fn amount(&self, _gross: f64) -> f64 {
        self.monthly
    }
}

pub fn parse_clock_payload(fields: &HashMap<String, Box<dyn Any>>) -> Option<ClockEvent> {
    let employee_id = fields.get("badge")?.downcast_ref::<String>()?.clone();
    let raw_hours = fields.get("hours")?;
    let hours = if let Some(h) = raw_hours.downcast_ref::<f64>() {
        *h
    } else {
        f64::from(*raw_hours.downcast_ref::<i32>()?)
    };
    Some(ClockEvent { employee_id, hours })
}

pub fn round_cents(amount: f64) -> i64 {
    (amount * 100.0).round() as i64
}

pub fn prorate_hours(hours: f64, worked_days: u32, period_days: u32) -> f64 {
    hours * f64::from(worked_days) / f64::from(period_days)
}

pub fn overtime_forecast(e: &Employee, weekly_hours: f64) -> f64 {
    let extra = prorate_hours(weekly_hours, 5, 7) - STANDARD_WEEK_HOURS;
    extra.max(0.0) * e.rate * OVERTIME_MULTIPLIER
}

pub fn holiday_accrual_preview(e: &Employee, days_worked: u32) -> f64 {
    prorate_hours(STANDARD_WEEK_HOURS, days_worked, 365) * e.rate
}

pub fn legacy_tax(gross: f64) -> f64 {
    let rate = LEGACY_TAX_BANDS
        .iter()
        .filter(|(floor, _)| gross >= *floor)
        .last()
        .map_or(0.0, |(_, rate)| *rate);
    gross * rate
}

pub fn is_hourly(e: &Employee) -> bool {
    e.contract.trim().to_lowercase() == "hourly"
}

pub fn run_payroll(
    employees: &[Employee],
    events: &[ClockEvent],
    deductions: &[Box<dyn Deduction>],
) -> Vec<String> {
    let mut issues = Vec::new();
    let mut hours: HashMap<&str, f64> = HashMap::new();
    for event in events {
        if !employees.iter().any(|e| e.id == event.employee_id) {
            issues.push(format!(
                "clock event for unknown badge {}",
                event.employee_id
            ));
            continue;
        }
        if event.hours <= 0.0 {
            issues.push(format!("non-positive hours for {}", event.employee_id));
            continue;
        }
        *hours.entry(event.employee_id.as_str()).or_insert(0.0) += event.hours;
    }
    let hourly_staff = employees.iter().filter(|e| is_hourly(e)).count();

    let countries = country_names();
    let mut lines = Vec::new();
    let mut total_gross = 0.0;
    let mut total_net = 0.0;
    let mut total_tax = 0.0;
    for e in employees {
        let worked = hours.get(e.id.as_str()).copied().unwrap_or(0.0);
        let gross = if e.contract == "hourly" {
            let regular = worked.min(STANDARD_WEEK_HOURS);
            let overtime = (worked - STANDARD_WEEK_HOURS).max(0.0);
            regular * e.rate + overtime * e.rate * OVERTIME_MULTIPLIER
        } else {
            e.rate
        };
        if gross == 0.0 {
            issues.push(format!("{} has no pay this period", e.name));
            continue;
        }

        let tax = gross * INCOME_TAX_RATE;
        let social = gross * SOCIAL_SECURITY_RATE;
        let mut other = 0.0;
        let mut breakdown = Vec::new();
        for d in deductions {
            let amount = d.amount(gross);
            other += amount;
            breakdown.push(format!("{} {}", d.label(), money(amount)));
        }
        let net = gross - tax - social - other;
        if net < 0.0 {
            issues.push(format!("{} has negative net pay", e.name));
        }

        let country = countries
            .get(e.country.as_str())
            .copied()
            .unwrap_or("Unknown");
        lines.push(format!("{} ({}, {})", e.name, e.id, country));
        lines.push(format!(
            "  gross {} tax {} social {}",
            money(gross),
            money(tax),
            money(social)
        ));
        lines.push(format!("  {}", breakdown.join(", ")));
        lines.push(format!("  net {}", money(net)));
        total_gross += gross;
        total_net += net;
        total_tax += tax;
    }

    lines.push(format!(
        "Staff {} ({} hourly)",
        employees.len(),
        hourly_staff
    ));
    lines.push(format!(
        "Total gross {} net {} tax withheld {}",
        money(total_gross),
        money(total_net),
        money(total_tax)
    ));
    for issue in &issues {
        lines.push(format!("Check: {issue}"));
    }
    lines
}

pub fn country_names() -> HashMap<&'static str, &'static str> {
    HashMap::from([
        ("AD", "Andorra"),
        ("AE", "United Arab Emirates"),
        ("AO", "Angola"),
        ("AR", "Argentina"),
        ("AT", "Austria"),
        ("AU", "Australia"),
        ("BE", "Belgium"),
        ("BG", "Bulgaria"),
        ("BO", "Bolivia"),
        ("BR", "Brazil"),
        ("CA", "Canada"),
        ("CH", "Switzerland"),
        ("CL", "Chile"),
        ("CN", "China"),
        ("CO", "Colombia"),
        ("CV", "Cape Verde"),
        ("CY", "Cyprus"),
        ("CZ", "Czechia"),
        ("DE", "Germany"),
        ("DK", "Denmark"),
        ("DZ", "Algeria"),
        ("EC", "Ecuador"),
        ("EE", "Estonia"),
        ("EG", "Egypt"),
        ("ES", "Spain"),
        ("FI", "Finland"),
        ("FR", "France"),
        ("GB", "United Kingdom"),
        ("GR", "Greece"),
        ("GW", "Guinea-Bissau"),
        ("HK", "Hong Kong"),
        ("HR", "Croatia"),
        ("HU", "Hungary"),
        ("ID", "Indonesia"),
        ("IE", "Ireland"),
        ("IL", "Israel"),
        ("IN", "India"),
        ("IS", "Iceland"),
        ("IT", "Italy"),
        ("JP", "Japan"),
        ("KE", "Kenya"),
        ("KR", "South Korea"),
        ("LT", "Lithuania"),
        ("LU", "Luxembourg"),
        ("LV", "Latvia"),
        ("MA", "Morocco"),
        ("MT", "Malta"),
        ("MX", "Mexico"),
        ("MY", "Malaysia"),
        ("MZ", "Mozambique"),
        ("NG", "Nigeria"),
        ("NL", "Netherlands"),
        ("NO", "Norway"),
        ("NZ", "New Zealand"),
        ("PE", "Peru"),
        ("PH", "Philippines"),
        ("PK", "Pakistan"),
        ("PL", "Poland"),
        ("PT", "Portugal"),
        ("PY", "Paraguay"),
        ("QA", "Qatar"),
        ("RO", "Romania"),
        ("RS", "Serbia"),
        ("SA", "Saudi Arabia"),
        ("SE", "Sweden"),
        ("SG", "Singapore"),
        ("SI", "Slovenia"),
        ("SK", "Slovakia"),
        ("ST", "Sao Tome and Principe"),
        ("TH", "Thailand"),
        ("TL", "Timor-Leste"),
        ("TN", "Tunisia"),
        ("TR", "Turkey"),
        ("TW", "Taiwan"),
        ("UA", "Ukraine"),
        ("US", "United States"),
        ("UY", "Uruguay"),
        ("VN", "Vietnam"),
        ("ZA", "South Africa"),
    ])
}

fn main() {
    let employees = vec![
        Employee {
            id: "E1".into(),
            name: "Marta Reis".into(),
            country: "PT".into(),
            contract: "hourly".into(),
            rate: 14.0,
        },
        Employee {
            id: "E2".into(),
            name: "Joel Kim".into(),
            country: "KR".into(),
            contract: "Hourly ".into(),
            rate: 16.0,
        },
        Employee {
            id: "E3".into(),
            name: "Ana Diaz".into(),
            country: "ES".into(),
            contract: "salaried".into(),
            rate: 2900.0,
        },
    ];
    let mut events = Vec::new();
    for (badge, hours) in [("E1", 44.0), ("E2", 38.5)] {
        let mut fields: HashMap<String, Box<dyn Any>> = HashMap::new();
        fields.insert("badge".into(), Box::new(String::from(badge)));
        fields.insert("hours".into(), Box::new(hours));
        events.extend(parse_clock_payload(&fields));
    }
    let deductions: Vec<Box<dyn Deduction>> = vec![
        Box::new(PensionContribution { percent: 4.0 }),
        Box::new(UnionDues { monthly: 12.5 }),
    ];
    println!(
        "{}",
        run_payroll(&employees, &events, &deductions).join("\n")
    );
}
