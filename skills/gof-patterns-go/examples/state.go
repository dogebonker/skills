package main

import "fmt"

// State is a typed enum; the transition table replaces State subclasses.
type State int

const (
	Pending State = iota
	Paid
	Shipped
	Cancelled
)

func (s State) String() string {
	return [...]string{"pending", "paid", "shipped", "cancelled"}[s]
}

var transitions = map[State][]State{
	Pending: {Paid, Cancelled},
	Paid:    {Shipped, Cancelled},
}

type Order struct{ state State }

func (o *Order) To(next State) error {
	for _, ok := range transitions[o.state] {
		if ok == next {
			o.state = next
			return nil
		}
	}
	return fmt.Errorf("cannot go from %s to %s", o.state, next)
}

func main() {
	o := &Order{}
	for _, next := range []State{Paid, Shipped, Cancelled} {
		if err := o.To(next); err != nil {
			fmt.Println("error:", err)
			continue
		}
		fmt.Println("now", o.state)
	}
}
