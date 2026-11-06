package fixture

import "testing"

func mustParse(t *testing.T, s string) int {
	t.Helper()
	n, err := Parse(s)
	if err != nil {
		t.Fatal(err)
	}
	return n
}

func TestMustParse(t *testing.T) {
	if mustParse(t, "7") != 7 {
		t.Fatal("want 7")
	}
}
