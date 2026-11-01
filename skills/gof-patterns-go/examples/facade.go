package main

import (
	"errors"
	"fmt"
)

// Subsystems with their own small APIs.
type inventory struct{}
type payments struct{}
type shipping struct{}

func (inventory) Reserve(sku string) error { fmt.Println("reserved", sku); return nil }
func (inventory) Release(sku string)       { fmt.Println("released", sku) }
func (payments) Charge(cents int) error {
	if cents > 10000 {
		return errors.New("card declined")
	}
	fmt.Println("charged", cents)
	return nil
}
func (shipping) Schedule(sku string) string {
	fmt.Println("shipment scheduled for", sku)
	return "TRACK-001"
}

// OrderService is the facade: one call hides the sequence and error handling.
type OrderService struct {
	inv  inventory
	pay  payments
	ship shipping
}

func (o OrderService) Place(sku string, cents int) (string, error) {
	if cents < 0 {
		return "", fmt.Errorf("invalid amount %d", cents)
	}
	if err := o.inv.Reserve(sku); err != nil {
		return "", fmt.Errorf("reserve: %w", err)
	}
	if err := o.pay.Charge(cents); err != nil {
		o.inv.Release(sku) // compensate the committed step
		return "", fmt.Errorf("charge: %w", err)
	}
	return o.ship.Schedule(sku), nil
}

func main() {
	tracking, err := OrderService{}.Place("book-7", 1999)
	fmt.Println(tracking, err)

	_, err = OrderService{}.Place("book-8", 50000)
	fmt.Println(err)
	_, err = OrderService{}.Place("book-9", -1)
	fmt.Println(err)
}
