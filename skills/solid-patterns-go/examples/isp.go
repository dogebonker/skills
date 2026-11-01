// ISP in Go: the consumer declares the one method it needs. Any type with
// that method satisfies it implicitly, including a three-line test fake.
package main

import "fmt"

type Order struct {
	ID    string
	Month int
	Cents int
}

// --- Violation: a fat, producer-side interface. monthlyRevenueV1 uses one
// method but every implementation and fake must provide all five.

type OrderRepository interface {
	Get(id string) (Order, error)
	ListByMonth(month int) ([]Order, error)
	Save(o Order) error
	Delete(id string) error
	Migrate() error
}

func monthlyRevenueV1(repo OrderRepository, month int) (int, error) {
	orders, err := repo.ListByMonth(month)
	if err != nil {
		return 0, err
	}
	sum := 0
	for _, o := range orders {
		sum += o.Cents
	}
	return sum, nil
}

// --- Fix: a one-method interface declared beside its only consumer.

type monthLister interface {
	ListByMonth(month int) ([]Order, error)
}

func monthlyRevenue(src monthLister, month int) (int, error) {
	orders, err := src.ListByMonth(month)
	if err != nil {
		return 0, err
	}
	sum := 0
	for _, o := range orders {
		sum += o.Cents
	}
	return sum, nil
}

// memRepo is the concrete store; it satisfies both interfaces without saying so.
type memRepo struct{ orders []Order }

func (r *memRepo) Get(id string) (Order, error) {
	for _, o := range r.orders {
		if o.ID == id {
			return o, nil
		}
	}
	return Order{}, fmt.Errorf("order %s not found", id)
}

func (r *memRepo) ListByMonth(month int) ([]Order, error) {
	var out []Order
	for _, o := range r.orders {
		if o.Month == month {
			out = append(out, o)
		}
	}
	return out, nil
}

func (r *memRepo) Save(o Order) error  { r.orders = append(r.orders, o); return nil }
func (r *memRepo) Delete(string) error { return nil }
func (r *memRepo) Migrate() error      { return nil }

// fixedOrders is all a test needs for the fixed version.
type fixedOrders []Order

func (f fixedOrders) ListByMonth(int) ([]Order, error) { return f, nil }

func main() {
	repo := &memRepo{}
	for _, o := range []Order{{"o1", 3, 1200}, {"o2", 3, 800}, {"o3", 4, 500}} {
		_ = repo.Save(o)
	}
	before, _ := monthlyRevenueV1(repo, 3)
	after, _ := monthlyRevenue(repo, 3)
	fake, _ := monthlyRevenue(fixedOrders{{"t1", 3, 1200}, {"t2", 3, 800}}, 3)
	fmt.Println("violation:", before, "fix:", after, "fake:", fake)
	fmt.Println("same output:", before == after && after == fake)
}
