package main

import (
	"fmt"
	"maps"
	"slices"
)

type Cloner[T any] interface{ Clone() T }

type Invoice struct {
	Customer string
	Lines    []string
	Meta     map[string]string
}

// Clone deep-copies reference fields; a plain struct copy would share them.
func (i Invoice) Clone() Invoice {
	c := i
	c.Lines = slices.Clone(i.Lines)
	c.Meta = maps.Clone(i.Meta)
	return c
}

func main() {
	var template Cloner[Invoice] = Invoice{
		Customer: "acme",
		Lines:    []string{"hosting"},
		Meta:     map[string]string{"currency": "EUR"},
	}
	a := template.Clone()
	a.Lines = append(a.Lines, "support")
	a.Meta["currency"] = "USD"

	fmt.Println("template:", template)
	fmt.Println("clone:   ", a)
}
