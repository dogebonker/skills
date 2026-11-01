// LSP in Go: an implementation must keep the promises of the interface it
// satisfies ("require no more, promise no less"). A method that always fails
// promises less, and callers start type-switching around it.
package main

import (
	"errors"
	"fmt"
	"strings"
)

// --- Violation: envFlags satisfies FlagStoreV1 but refuses Set, so the
// caller must know about the concrete type.

type FlagStoreV1 interface {
	Enabled(name string) bool
	Set(name string, on bool) error
}

type envFlags struct{ snapshot map[string]bool }

func (e envFlags) Enabled(name string) bool { return e.snapshot[name] }
func (envFlags) Set(string, bool) error     { return errors.New("env flags are read-only") }

type memFlags struct{ flags map[string]bool }

func (m *memFlags) Enabled(name string) bool { return m.flags[name] }
func (m *memFlags) Set(name string, on bool) error {
	m.flags[name] = on
	return nil
}

func applyDefaultsV1(stores []FlagStoreV1, defaults map[string]bool) {
	for _, s := range stores {
		if _, readOnly := s.(envFlags); readOnly { // the LSP smell
			continue
		}
		for name, on := range defaults {
			_ = s.Set(name, on)
		}
	}
}

// --- Fix: each type promises only what it does. envFlags satisfies FlagReader
// and nothing more, so no caller can be handed a Set that fails.

type FlagReader interface{ Enabled(name string) bool }

type FlagWriter interface {
	FlagReader
	Set(name string, on bool) error
}

func applyDefaults(stores []FlagWriter, defaults map[string]bool) error {
	for _, s := range stores {
		for name, on := range defaults {
			if err := s.Set(name, on); err != nil {
				return err
			}
		}
	}
	return nil
}

func report(readers []FlagReader, names []string) string {
	var b strings.Builder
	for i, r := range readers {
		for _, n := range names {
			fmt.Fprintf(&b, " store%d.%s=%t", i, n, r.Enabled(n))
		}
	}
	return b.String()
}

func main() {
	defaults := map[string]bool{"dark_mode": true, "new_checkout": false}
	names := []string{"dark_mode", "new_checkout"}

	env1, mem1 := envFlags{map[string]bool{"new_checkout": true}}, &memFlags{map[string]bool{}}
	applyDefaultsV1([]FlagStoreV1{env1, mem1}, defaults)
	before := report([]FlagReader{env1, mem1}, names)

	env2, mem2 := envFlags{map[string]bool{"new_checkout": true}}, &memFlags{map[string]bool{}}
	if err := applyDefaults([]FlagWriter{mem2}, defaults); err != nil {
		panic(err)
	}
	after := report([]FlagReader{env2, mem2}, names)
	fmt.Println("violation:", before)
	fmt.Println("fix:      ", after)
	fmt.Println("same output:", before == after)
}
