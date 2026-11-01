// SRP in Go: split by reason to change. Here the three jobs are functions;
// in a real codebase each would live in a package named for what it provides
// (orders, billing, report), never in "utils".
package main

import (
	"bufio"
	"fmt"
	"strconv"
	"strings"
)

type Order struct {
	Customer string
	Cents    int
}

// --- Violation: one function parses input, applies the finance rule and
// formats output. A tax change (finance) and a layout change (ops) both edit it.

func invoiceSummaryV1(csv string) (string, error) {
	var b strings.Builder
	total := 0
	sc := bufio.NewScanner(strings.NewReader(csv))
	for sc.Scan() {
		parts := strings.Split(sc.Text(), ",")
		cents, err := strconv.Atoi(parts[1])
		if err != nil {
			return "", err
		}
		withTax := cents + cents*23/100
		total += withTax
		fmt.Fprintf(&b, "%-8s %8.2f\n", parts[0], float64(withTax)/100)
	}
	fmt.Fprintf(&b, "%-8s %8.2f\n", "TOTAL", float64(total)/100)
	return b.String(), sc.Err()
}

// --- Fix: each function has one reason to change.

// parseOrders changes when the input format changes.
func parseOrders(csv string) ([]Order, error) {
	var orders []Order
	sc := bufio.NewScanner(strings.NewReader(csv))
	for sc.Scan() {
		customer, amount, _ := strings.Cut(sc.Text(), ",")
		cents, err := strconv.Atoi(amount)
		if err != nil {
			return nil, fmt.Errorf("parse %q: %w", sc.Text(), err)
		}
		orders = append(orders, Order{customer, cents})
	}
	return orders, sc.Err()
}

// withVAT changes when finance changes the tax rule.
func withVAT(cents int) int { return cents + cents*23/100 }

// renderSummary changes when the report layout changes.
func renderSummary(orders []Order, tax func(int) int) string {
	var b strings.Builder
	total := 0
	for _, o := range orders {
		t := tax(o.Cents)
		total += t
		fmt.Fprintf(&b, "%-8s %8.2f\n", o.Customer, float64(t)/100)
	}
	fmt.Fprintf(&b, "%-8s %8.2f\n", "TOTAL", float64(total)/100)
	return b.String()
}

func invoiceSummary(csv string) (string, error) {
	orders, err := parseOrders(csv)
	if err != nil {
		return "", err
	}
	return renderSummary(orders, withVAT), nil
}

func main() {
	input := "acme,10000\nglobex,2550\ninitech,999"
	before, err1 := invoiceSummaryV1(input)
	after, err2 := invoiceSummary(input)
	if err1 != nil || err2 != nil {
		panic(fmt.Sprint(err1, err2))
	}
	fmt.Print("violation:\n", before, "fix:\n", after)
	fmt.Println("same output:", before == after)
}
