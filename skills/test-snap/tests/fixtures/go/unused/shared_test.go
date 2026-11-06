package unused

import "testing"

// Deleting the only subtest leaves `want` declared and not used: a compile error.
func TestShared(t *testing.T) {
	want := 3
	t.Run("uses want", func(t *testing.T) {
		if 1+2 != want {
			t.Fatal(want)
		}
	})
}
