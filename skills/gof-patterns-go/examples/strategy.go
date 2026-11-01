package main

import (
	"fmt"
	"sort"
)

// Pricing is a function type; no interface or struct needed.
type Pricing func(base float64) float64

func Regular(base float64) float64     { return base }
func BlackFriday(base float64) float64 { return base * 0.7 }
func Loyalty(pct float64) Pricing {
	return func(base float64) float64 { return base * (1 - pct/100) }
}

func total(items []float64, p Pricing) (sum float64) {
	for _, it := range items {
		sum += p(it)
	}
	return sum
}

func main() {
	cart := []float64{20, 35.5, 10}
	strategies := map[string]Pricing{
		"regular":      Regular,
		"black friday": BlackFriday,
		"loyalty 10%":  Loyalty(10),
	}
	names := make([]string, 0, len(strategies))
	for n := range strategies {
		names = append(names, n)
	}
	sort.Strings(names)
	for _, n := range names {
		fmt.Printf("%-13s %.2f\n", n, total(cart, strategies[n]))
	}
}
