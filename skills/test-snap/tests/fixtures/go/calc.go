// Package fixture is a tiny calculator used by the test-snap fixtures.
package fixture

import (
	"fmt"
	"strconv"
)

// Add returns a + b.
func Add(a, b int) int { return a + b }

// Parse parses a decimal integer.
func Parse(s string) (int, error) {
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("parse %q: %w", s, err)
	}
	return n, nil
}
