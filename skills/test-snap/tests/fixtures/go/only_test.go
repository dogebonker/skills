package fixture

import "testing"

// TestOnly is the only test in this file.
func TestOnly(t *testing.T) {
	if Add(2, 2) != 4 {
		t.Fatal("math")
	}
}
