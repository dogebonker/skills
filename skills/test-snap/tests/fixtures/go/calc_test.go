package fixture

import (
	"strings"
	"testing"
)

// TestAdd is a table test with non-literal subtest names.
func TestAdd(t *testing.T) {
	cases := []struct {
		name string
		a, b int
		want int
	}{
		{"zero", 0, 0, 0},
		{"positive", 1, 2, 3},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := Add(tc.a, tc.b); got != tc.want {
				t.Fatalf("Add(%d, %d) = %d, want %d", tc.a, tc.b, got, tc.want)
			}
		})
	}
}

func TestParse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		if n, err := Parse(strings.TrimSpace(" 42 ")); err != nil || n != 42 {
			t.Fatal(n, err)
		}
	})

	t.Run("invalid", func(t *testing.T) {
		t.Run(`empty`, func(t *testing.T) {
			if _, err := Parse(""); err == nil {
				t.Fatal("want error")
			}
		})

		t.Run("letters ü", func(t *testing.T) {
			_, err := Parse("abc")
			if err == nil || !strings.Contains(err.Error(), "abc") {
				t.Fatal(err)
			}
		})
	})
}

// TestMain is not a test.
func TestMain(m *testing.M) { m.Run() }

func BenchmarkAdd(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Add(1, 2)
	}
}
