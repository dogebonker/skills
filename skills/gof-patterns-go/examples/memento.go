package main

import "fmt"

// Snapshot is opaque to callers: its fields are unexported.
type Snapshot struct{ cells [][]int }

type Grid struct{ cells [][]int }

func clone(c [][]int) [][]int {
	out := make([][]int, len(c))
	for i, row := range c {
		out[i] = append([]int(nil), row...)
	}
	return out
}

func (g *Grid) Save() Snapshot     { return Snapshot{cells: clone(g.cells)} }
func (g *Grid) Restore(s Snapshot) { g.cells = clone(s.cells) }

func main() {
	g := &Grid{cells: [][]int{{1, 2}, {3, 4}}}
	var saved []Snapshot

	saved = append(saved, g.Save())
	g.cells[0][0] = 99
	saved = append(saved, g.Save())
	g.cells[1][1] = -1
	fmt.Println("now:", g.cells)

	g.Restore(saved[1])
	fmt.Println("undo 1:", g.cells)
	g.Restore(saved[0])
	fmt.Println("undo 2:", g.cells)
}
