package main

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"fleet/service"
)

const (
	serviceIntervalKm  = 15000
	electricIntervalKm = 30000
	labourHoursPerJob  = 1.5
	urgentCodePrefix   = "P03"
	dueSoonKm          = 2000
)

var legacyIntervalsKm = map[string]int{"Transit": 20000, "Sprinter": 25000, "Ducato": 18000}

type Vehicle struct {
	ID, Plate, Model, FuelType string
	OdometerKm, LastServiceKm  int
}

type Ping struct {
	VehicleID  string
	OdometerKm int
	FaultCodes []string
}

type Workshop interface {
	Quote(job service.Job) float64
	WorkOrder(job service.Job) string
}

type depot struct{ hourlyRate float64 }

func (d depot) Quote(job service.Job) float64 { return job.Hours * d.hourlyRate }

func (d depot) WorkOrder(job service.Job) string {
	return fmt.Sprintf("depot: %s, %.1f h", job.Plate, job.Hours)
}

func parseTelematicsPayload(raw []byte) (Ping, error) {
	var m map[string]any
	if err := json.Unmarshal(raw, &m); err != nil {
		return Ping{}, err
	}
	ping := Ping{VehicleID: fmt.Sprint(m["unit"])}
	switch v := m["odo"].(type) {
	case float64:
		ping.OdometerKm = int(v)
	case string:
		fmt.Sscan(v, &ping.OdometerKm)
	}
	if codes, ok := m["dtc"].([]any); ok {
		for _, c := range codes {
			ping.FaultCodes = append(ping.FaultCodes, fmt.Sprint(c))
		}
	}
	return ping, nil
}

func normalizePlate(plate string) string {
	return strings.ToUpper(strings.TrimSpace(plate))
}

func garageSlots(v Vehicle) int {
	return (v.OdometerKm-v.LastServiceKm)/serviceIntervalKm + 1
}

func plannedDowntime(vehicles []Vehicle) int {
	total := 0
	for _, v := range vehicles {
		total += garageSlots(v)
	}
	return total
}

func idleCost(vehicles []Vehicle, dailyRate float64) float64 {
	cost := 0.0
	for _, v := range vehicles {
		cost += float64(garageSlots(v)) * dailyRate
	}
	return cost
}

func legacyServiceInterval(model string) int {
	if km, ok := legacyIntervalsKm[model]; ok {
		return km
	}
	return serviceIntervalKm
}

func isElectric(v Vehicle) bool {
	return strings.EqualFold(strings.TrimSpace(v.FuelType), "electric")
}

func planMaintenanceRun(vehicles []Vehicle, pings []Ping, shops []Workshop) ([]string, []string) {
	var issues []string
	byID := map[string]*Vehicle{}
	for i := range vehicles {
		byID[vehicles[i].ID] = &vehicles[i]
	}
	for _, p := range pings {
		v, ok := byID[p.VehicleID]
		if !ok {
			issues = append(issues, "ping from unknown unit "+p.VehicleID)
			continue
		}
		if p.OdometerKm < v.OdometerKm {
			issues = append(issues, fmt.Sprintf("%s: odometer went backwards", v.ID))
			continue
		}
		v.OdometerKm = p.OdometerKm
	}

	var due []*Vehicle
	var dueSoon []string
	electric := 0
	for i := range vehicles {
		v := &vehicles[i]
		if isElectric(*v) {
			electric++
		}
		interval := serviceIntervalKm
		if v.FuelType == "electric" {
			interval = electricIntervalKm
		}
		remaining := interval - (v.OdometerKm - v.LastServiceKm)
		if remaining <= 0 {
			due = append(due, v)
		} else if remaining <= dueSoonKm {
			dueSoon = append(dueSoon, fmt.Sprintf("%s in %d km", v.ID, remaining))
		}
	}

	descriptions := troubleCodes()
	var faults []string
	urgent := map[string]bool{}
	for _, p := range pings {
		for _, code := range p.FaultCodes {
			text, known := descriptions[code]
			if !known {
				text = "unknown code"
			}
			faults = append(faults, fmt.Sprintf("%s %s: %s", p.VehicleID, code, text))
			urgent[p.VehicleID] = urgent[p.VehicleID] || strings.HasPrefix(code, urgentCodePrefix)
		}
	}

	var orders []string
	total := 0.0
	for _, v := range due {
		job := service.Job{Plate: v.Plate, Hours: labourHoursPerJob}
		best := shops[0]
		for _, s := range shops[1:] {
			if s.Quote(job) < best.Quote(job) {
				best = s
			}
		}
		total += best.Quote(job)
		orders = append(orders, best.WorkOrder(job))
	}
	sort.Strings(orders)

	lines := []string{
		fmt.Sprintf("Fleet of %d (%d electric), %d due for service", len(vehicles), electric, len(due)),
		fmt.Sprintf("Planned labour cost %.2f EUR", total),
	}
	lines = append(lines, orders...)
	if len(dueSoon) > 0 {
		lines = append(lines, "Due soon: "+strings.Join(dueSoon, ", "))
	}
	for id, isUrgent := range urgent {
		if isUrgent {
			lines = append(lines, "Pull from service today: "+id)
		}
	}
	lines = append(lines, faults...)
	return lines, issues
}

func troubleCodes() map[string]string {
	return map[string]string{
		"P0100": "Mass air flow circuit malfunction",
		"P0101": "Mass air flow circuit range or performance",
		"P0102": "Mass air flow circuit low input",
		"P0103": "Mass air flow circuit high input",
		"P0105": "Manifold pressure circuit malfunction",
		"P0106": "Manifold pressure range or performance",
		"P0107": "Manifold pressure circuit low input",
		"P0108": "Manifold pressure circuit high input",
		"P0110": "Intake air temperature circuit malfunction",
		"P0112": "Intake air temperature circuit low input",
		"P0113": "Intake air temperature circuit high input",
		"P0115": "Coolant temperature circuit malfunction",
		"P0116": "Coolant temperature range or performance",
		"P0117": "Coolant temperature circuit low input",
		"P0118": "Coolant temperature circuit high input",
		"P0120": "Throttle position sensor circuit malfunction",
		"P0121": "Throttle position sensor range or performance",
		"P0122": "Throttle position sensor low input",
		"P0123": "Throttle position sensor high input",
		"P0125": "Insufficient coolant temperature for closed loop",
		"P0128": "Coolant thermostat below regulating temperature",
		"P0130": "Oxygen sensor circuit bank 1 sensor 1",
		"P0131": "Oxygen sensor low voltage bank 1 sensor 1",
		"P0132": "Oxygen sensor high voltage bank 1 sensor 1",
		"P0133": "Oxygen sensor slow response bank 1 sensor 1",
		"P0134": "Oxygen sensor no activity bank 1 sensor 1",
		"P0135": "Oxygen sensor heater circuit bank 1 sensor 1",
		"P0136": "Oxygen sensor circuit bank 1 sensor 2",
		"P0141": "Oxygen sensor heater circuit bank 1 sensor 2",
		"P0171": "System too lean bank 1",
		"P0172": "System too rich bank 1",
		"P0174": "System too lean bank 2",
		"P0175": "System too rich bank 2",
		"P0200": "Injector circuit malfunction",
		"P0201": "Injector circuit cylinder 1",
		"P0202": "Injector circuit cylinder 2",
		"P0203": "Injector circuit cylinder 3",
		"P0204": "Injector circuit cylinder 4",
		"P0217": "Engine overheat condition",
		"P0219": "Engine overspeed condition",
		"P0230": "Fuel pump primary circuit",
		"P0234": "Turbocharger overboost condition",
		"P0299": "Turbocharger underboost",
		"P0300": "Random or multiple cylinder misfire",
		"P0301": "Cylinder 1 misfire",
		"P0302": "Cylinder 2 misfire",
		"P0303": "Cylinder 3 misfire",
		"P0304": "Cylinder 4 misfire",
		"P0305": "Cylinder 5 misfire",
		"P0306": "Cylinder 6 misfire",
		"P0325": "Knock sensor circuit bank 1",
		"P0335": "Crankshaft position sensor circuit",
		"P0340": "Camshaft position sensor circuit",
		"P0380": "Glow plug circuit",
		"P0400": "Exhaust gas recirculation flow",
		"P0401": "Exhaust gas recirculation flow insufficient",
		"P0402": "Exhaust gas recirculation flow excessive",
		"P0420": "Catalyst efficiency below threshold bank 1",
		"P0430": "Catalyst efficiency below threshold bank 2",
		"P0440": "Evaporative emission system malfunction",
		"P0442": "Evaporative emission small leak",
		"P0446": "Evaporative emission vent control circuit",
		"P0455": "Evaporative emission large leak",
		"P0456": "Evaporative emission very small leak",
		"P0500": "Vehicle speed sensor malfunction",
		"P0505": "Idle air control system",
		"P0506": "Idle speed lower than expected",
		"P0507": "Idle speed higher than expected",
		"P0562": "System voltage low",
		"P0563": "System voltage high",
		"P0600": "Serial communication link",
		"P0700": "Transmission control system malfunction",
		"P0705": "Transmission range sensor circuit",
		"P0715": "Input turbine speed sensor circuit",
		"P0720": "Output speed sensor circuit",
		"P0730": "Incorrect gear ratio",
		"P0740": "Torque converter clutch circuit",
		"P0741": "Torque converter clutch stuck off",
		"P0750": "Shift solenoid A malfunction",
		"P0755": "Shift solenoid B malfunction",
	}
}

func main() {
	vehicles := []Vehicle{
		{ID: "V1", Plate: "aa 12 bb", Model: "Transit", FuelType: "diesel", OdometerKm: 41000, LastServiceKm: 30000},
		{ID: "V2", Plate: "cc 34 dd", Model: "eVito", FuelType: "Electric ", OdometerKm: 52000, LastServiceKm: 30000},
		{ID: "V3", Plate: "ee 56 ff", Model: "Ducato", FuelType: "electric", OdometerKm: 64000, LastServiceKm: 30000},
	}
	var pings []Ping
	for _, raw := range []string{`{"unit":"V1","odo":45500,"dtc":["P0301"]}`, `{"unit":"V3","odo":"64100","dtc":[]}`} {
		ping, err := parseTelematicsPayload([]byte(raw))
		if err != nil {
			fmt.Println(err)
			continue
		}
		pings = append(pings, ping)
	}
	shops := []Workshop{depot{hourlyRate: 52}, service.Shop{Name: "Oficina Norte", HourlyRate: 40, CalloutFee: 15}}
	lines, issues := planMaintenanceRun(vehicles, pings, shops)
	fmt.Println(strings.Join(lines, "\n"), issues)
}
