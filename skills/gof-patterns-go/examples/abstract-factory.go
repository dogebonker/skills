package main

import "fmt"

type Charger interface{ Charge(cents int) string }
type Refunder interface{ Refund(cents int) string }

// PaymentFactory creates a family of related products that must match.
type PaymentFactory interface {
	NewCharger() Charger
	NewRefunder() Refunder
}

type stripeCharger struct{}
type stripeRefunder struct{}

func (stripeCharger) Charge(c int) string  { return fmt.Sprintf("stripe charge %d", c) }
func (stripeRefunder) Refund(c int) string { return fmt.Sprintf("stripe refund %d", c) }

type stripeFactory struct{}

func (stripeFactory) NewCharger() Charger   { return stripeCharger{} }
func (stripeFactory) NewRefunder() Refunder { return stripeRefunder{} }

type adyenCharger struct{}
type adyenRefunder struct{}

func (adyenCharger) Charge(c int) string  { return fmt.Sprintf("adyen capture %d", c) }
func (adyenRefunder) Refund(c int) string { return fmt.Sprintf("adyen reversal %d", c) }

type adyenFactory struct{}

func (adyenFactory) NewCharger() Charger   { return adyenCharger{} }
func (adyenFactory) NewRefunder() Refunder { return adyenRefunder{} }

// checkout depends only on the factory interface.
func checkout(f PaymentFactory, cents int) {
	fmt.Println(f.NewCharger().Charge(cents))
	fmt.Println(f.NewRefunder().Refund(cents / 2))
}

func main() {
	for _, f := range []PaymentFactory{stripeFactory{}, adyenFactory{}} {
		checkout(f, 2000)
	}
}
