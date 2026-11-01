package main

import (
	"fmt"
	"sync"
)

// Icon is the shared, immutable intrinsic state.
type Icon struct {
	Name   string
	Pixels []byte
}

var (
	mu    sync.Mutex
	cache = map[string]*Icon{}
)

// IconFor returns one shared Icon per name.
func IconFor(name string) *Icon {
	mu.Lock()
	defer mu.Unlock()
	if ic, ok := cache[name]; ok {
		return ic
	}
	ic := &Icon{Name: name, Pixels: make([]byte, 1024)}
	cache[name] = ic
	return ic
}

// Marker holds extrinsic state (position) and points at the shared Icon.
type Marker struct {
	X, Y int
	Icon *Icon
}

func main() {
	var markers []Marker
	for i := range 1000 {
		name := []string{"pin", "flag", "star"}[i%3]
		markers = append(markers, Marker{X: i, Y: i * 2, Icon: IconFor(name)})
	}
	var wg sync.WaitGroup
	for range 4 {
		wg.Go(func() { IconFor("pin") })
	}
	wg.Wait()
	fmt.Println("markers:", len(markers), "icons allocated:", len(cache))
	fmt.Println("shared:", markers[0].Icon == markers[3].Icon)
}
