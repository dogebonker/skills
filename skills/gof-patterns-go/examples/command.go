package main

import "fmt"

// Command is a function value; it can be queued, logged or undone via a pair.
type Command struct {
	Name string
	Do   func()
	Undo func()
}

type Editor struct{ text string }

func (e *Editor) Append(s string) Command {
	return Command{
		Name: "append " + s,
		Do:   func() { e.text += s },
		Undo: func() { e.text = e.text[:len(e.text)-len(s)] },
	}
}

func main() {
	ed := &Editor{}
	var history []Command

	for _, c := range []Command{ed.Append("hello"), ed.Append(", world")} {
		c.Do()
		history = append(history, c)
		fmt.Printf("%-16s -> %q\n", c.Name, ed.text)
	}
	for len(history) > 0 {
		last := history[len(history)-1]
		history = history[:len(history)-1]
		last.Undo()
		fmt.Printf("undo %-11s -> %q\n", last.Name, ed.text)
	}
}
