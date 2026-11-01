package main

import "fmt"

// Shape is a closed set of types; a type switch is the idiomatic visitor.
type Shape interface{ isShape() }

type Circle struct{ R float64 }
type Rect struct{ W, H float64 }

func (Circle) isShape() {}
func (Rect) isShape()   {}

// Each operation is a plain function; adding one needs no change to shapes.
func area(s Shape) float64 {
	switch v := s.(type) {
	case Circle:
		return 3.14159 * v.R * v.R
	case Rect:
		return v.W * v.H
	default:
		panic(fmt.Sprintf("unhandled shape %T", s))
	}
}

func describe(s Shape) string {
	switch v := s.(type) {
	case Circle:
		return fmt.Sprintf("circle r=%.1f", v.R)
	case Rect:
		return fmt.Sprintf("rect %.1fx%.1f", v.W, v.H)
	default:
		panic(fmt.Sprintf("unhandled shape %T", s))
	}
}

func main() {
	for _, s := range []Shape{Circle{2}, Rect{3, 4}} {
		fmt.Printf("%s area=%.2f\n", describe(s), area(s))
	}
}
