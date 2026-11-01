package main

import (
	"fmt"
	"io"
	"os"
	"slices"
	"strconv"
	"strings"
)

type Product struct {
	SKU             string
	WeightKg, Price float64
}

type Box struct {
	Label    string
	TareKg   float64
	Contents []any
}

func totalWeight(item any) float64 {
	switch v := item.(type) {
	case Product:
		return v.WeightKg
	case Box:
		w := v.TareKg
		for _, c := range v.Contents {
			w += totalWeight(c)
		}
		return w
	}
	panic(fmt.Sprintf("unexpected item %T", item))
}

type StockStore interface {
	Get(sku string) int
	Set(sku string, qty int)
}

type memoryStore struct{ qty map[string]int }

func (s *memoryStore) Get(sku string) int      { return s.qty[sku] }
func (s *memoryStore) Set(sku string, qty int) { s.qty[sku] = qty }

type Warehouse struct {
	store StockStore
	log   []string
}

func (w *Warehouse) Execute(line string) (string, error) {
	parts := append(strings.Fields(line), "", "")
	sku, n := parts[1], 0
	n, _ = strconv.Atoi(parts[2])
	switch parts[0] {
	case "receive":
		w.store.Set(sku, w.store.Get(sku)+n)
	case "ship":
		if w.store.Get(sku) < n {
			return "", fmt.Errorf("not enough %s", sku)
		}
		w.store.Set(sku, w.store.Get(sku)-n)
	case "move":
		w.store.Set(parts[2], w.store.Get(parts[2])+w.store.Get(sku))
		w.store.Set(sku, 0)
	case "count":
		return strconv.Itoa(w.store.Get(sku)), nil
	default:
		return "", fmt.Errorf("unknown operation %q", parts[0])
	}
	w.log = append(w.log, line)
	return "", nil
}

func unitFactor(unit string) float64 {
	switch unit {
	case "kg":
		return 1
	case "lb":
		return 0.4536
	case "oz":
		return 0.02835
	}
	return 0
}

type Shipment struct {
	ID, From, To, Notes                 string
	WeightKg                            float64
	Insured, SignatureRequired, Fragile bool
}

func NewShipment(id, from, to string, weightKg float64, insured, signatureRequired, fragile bool, notes string) *Shipment {
	return &Shipment{id, from, to, notes, weightKg, insured, signatureRequired, fragile}
}

type NotFoundError struct{ SKU string }

func (e *NotFoundError) Error() string { return "not found: " + e.SKU }

func httpStatus(err error) int {
	switch err.(type) {
	case *NotFoundError:
		return 404
	default:
		return 500
	}
}

func exportCSV(w io.Writer, products []Product) {
	sorted := slices.SortedFunc(slices.Values(products), func(a, b Product) int { return strings.Compare(a.SKU, b.SKU) })
	fmt.Fprintln(w, "sku,weight,price")
	for _, p := range sorted {
		fmt.Fprintf(w, "%s,%.2f,%.2f\n", p.SKU, p.WeightKg, p.Price)
	}
	fmt.Fprintf(w, "total,%d,\n", len(sorted))
}

func exportMarkdown(w io.Writer, products []Product) {
	sorted := slices.SortedFunc(slices.Values(products), func(a, b Product) int { return strings.Compare(a.SKU, b.SKU) })
	fmt.Fprintln(w, "| SKU | Weight | Price |\n|---|---|---|")
	for _, p := range sorted {
		fmt.Fprintf(w, "| %s | %.2f kg | %.2f |\n", p.SKU, p.WeightKg, p.Price)
	}
	fmt.Fprintf(w, "\n%d products\n", len(sorted))
}

func exportHTML(w io.Writer, products []Product) {
	sorted := slices.SortedFunc(slices.Values(products), func(a, b Product) int { return strings.Compare(a.SKU, b.SKU) })
	fmt.Fprintln(w, "<table><tr><th>SKU</th><th>Weight</th><th>Price</th></tr>")
	for _, p := range sorted {
		fmt.Fprintf(w, "<tr><td>%s</td><td>%.2f</td><td>%.2f</td></tr>\n", p.SKU, p.WeightKg, p.Price)
	}
	fmt.Fprintf(w, "</table><p>%d products</p>\n", len(sorted))
}

func main() {
	w := &Warehouse{store: &memoryStore{qty: map[string]int{}}}
	for _, line := range []string{"receive A1 10", "ship A1 3", "move A1 B2", "count B2"} {
		fmt.Println(w.Execute(line))
	}
	box := Box{Label: "crate", TareKg: 2, Contents: []any{Product{"A1", 1.5, 20}, Box{"inner", 0.5, []any{Product{"B2", 3, 45}}}}}
	fmt.Println(totalWeight(box), unitFactor("lb"), httpStatus(&NotFoundError{SKU: "Z9"}))
	s := NewShipment("S-1", "Lisbon", "Porto", 3.2, false, false, false, "")
	t := NewShipment("S-2", "Porto", "Faro", 12, true, true, false, "glassware")
	exportCSV(os.Stdout, []Product{{"B2", 3, 45}, {"A1", 1.5, 20}})
	fmt.Println(s.ID, t.Insured)
	runExtras()
}

func parseReceiveForm(form map[string]string) (string, int, error) {
	sku := strings.ToUpper(strings.TrimSpace(form["sku"]))
	if len(sku) != 6 || !strings.HasPrefix(sku, "SK") {
		return "", 0, fmt.Errorf("invalid sku %q", sku)
	}
	qty, err := strconv.Atoi(form["qty"])
	if err != nil || qty <= 0 {
		return "", 0, fmt.Errorf("invalid quantity %q", form["qty"])
	}
	return sku, qty, nil
}

func saveStock(s *memoryStore, sku string, qty int) error {
	if len(sku) != 6 || sku[:2] != "SK" {
		return fmt.Errorf("sku %s must be 6 characters starting with SK", sku)
	}
	s.Set(sku, qty)
	return nil
}

func writeDailyReport(path string, products []Product, stock map[string]int) error {
	total := 0.0
	for _, p := range products {
		total += p.Price * float64(stock[p.SKU])
	}
	vat := total * 0.23
	var b strings.Builder
	fmt.Fprintf(&b, "Stock value %.2f EUR (VAT %.2f)\n", total, vat)
	for _, p := range products {
		fmt.Fprintf(&b, "%-8s %4d %8.2f\n", p.SKU, stock[p.SKU], p.Price)
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.WriteString(b.String())
	return err
}

var weightCache = map[string]float64{}

func cachedWeight(b Box) float64 {
	if w, ok := weightCache[b.Label]; ok {
		return w
	}
	w := totalWeight(b)
	weightCache[b.Label] = w
	return w
}

const linesPerPickList = 40
const lowStockThreshold = 40

type Dimensions struct{ L, W, H float64 }

func (d Dimensions) Volume() float64            { return d.L * d.W * d.H }
func (d Dimensions) Surface() float64           { return 2 * (d.L*d.W + d.L*d.H + d.W*d.H) }
func (d Dimensions) Fits(in Dimensions) bool    { return d.L <= in.L && d.W <= in.W && d.H <= in.H }
func (d Dimensions) Rotate() Dimensions         { return Dimensions{d.W, d.L, d.H} }
func (d Dimensions) Scale(f float64) Dimensions { return Dimensions{d.L * f, d.W * f, d.H * f} }
func (d Dimensions) Longest() float64           { return max(d.L, d.W, d.H) }
func (d Dimensions) String() string             { return fmt.Sprintf("%.0fx%.0fx%.0f cm", d.L, d.W, d.H) }

type Notifier interface {
	Notify(msg string) error
}

type emailNotifier struct{ to string }
type slackNotifier struct{ channel string }

func (n emailNotifier) Notify(msg string) error { fmt.Println("mail", n.to, msg); return nil }
func (n slackNotifier) Notify(msg string) error { fmt.Println("slack", n.channel, msg); return nil }

func alertLowStock(notifiers []Notifier, store StockStore, skus []string) {
	for _, sku := range skus {
		if store.Get(sku) < lowStockThreshold {
			for _, n := range notifiers {
				_ = n.Notify(fmt.Sprintf("%s below %d", sku, lowStockThreshold))
			}
		}
	}
}

func runExtras() {
	sku, qty, err := parseReceiveForm(map[string]string{"sku": " sk1234 ", "qty": "5"})
	store := &memoryStore{qty: map[string]int{}}
	fmt.Println(sku, qty, err, saveStock(store, sku, qty), linesPerPickList)
	fmt.Println(writeDailyReport(os.DevNull, []Product{{"SK1234", 1, 9.5}}, map[string]int{"SK1234": qty}))
	fmt.Println(cachedWeight(Box{Label: "c1", TareKg: 1}), Dimensions{30, 20, 10}.Rotate().Fits(Dimensions{40, 40, 40}))
	alertLowStock([]Notifier{emailNotifier{"ops@example.com"}, slackNotifier{"#stock"}}, store, []string{sku})
}
