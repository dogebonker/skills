package main

import (
	"fmt"
	"iter"
)

type Playlist struct{ tracks []string }

// All yields every track in order.
func (p *Playlist) All() iter.Seq2[int, string] {
	return func(yield func(int, string) bool) {
		for i, t := range p.tracks {
			if !yield(i, t) {
				return
			}
		}
	}
}

// Shuffled-style alternative traversal: reverse order, same consumer code.
func (p *Playlist) Reverse() iter.Seq[string] {
	return func(yield func(string) bool) {
		for i := len(p.tracks) - 1; i >= 0; i-- {
			if !yield(p.tracks[i]) {
				return
			}
		}
	}
}

func main() {
	p := &Playlist{tracks: []string{"intro", "verse", "chorus", "outro"}}
	for i, t := range p.All() {
		if i == 2 {
			break // early exit is honored by the iterator
		}
		fmt.Println(i, t)
	}
	for t := range p.Reverse() {
		fmt.Println("rev", t)
	}
}
