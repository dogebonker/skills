package main

import "fmt"

// Node is implemented by both leaves and containers.
type Node interface {
	Size() int
	Print(indent string)
}

type file struct {
	name string
	size int
}

func (f file) Size() int { return f.size }
func (f file) Print(indent string) {
	fmt.Printf("%s%s (%d)\n", indent, f.name, f.size)
}

type dir struct {
	name     string
	children []Node
}

func (d *dir) Add(n ...Node) *dir { d.children = append(d.children, n...); return d }

func (d *dir) Size() (total int) {
	for _, c := range d.children {
		total += c.Size()
	}
	return total
}

func (d *dir) Print(indent string) {
	fmt.Printf("%s%s/ (%d)\n", indent, d.name, d.Size())
	for _, c := range d.children {
		c.Print(indent + "  ")
	}
}

func main() {
	root := (&dir{name: "project"}).Add(
		file{"main.go", 120},
		(&dir{name: "internal"}).Add(file{"db.go", 300}, file{"api.go", 250}),
	)
	root.Print("")
}
