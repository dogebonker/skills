// OCP in Go: the exporter loop depends on a small interface, so a new format
// is a new type plus one registry line in main; the loop is never edited.
package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"strconv"
)

type Row struct {
	SKU   string `json:"sku"`
	Units int    `json:"units"`
}

// --- Violation: every new format edits this switch and retests every format.

func exportV1(w io.Writer, format string, rows []Row) error {
	switch format {
	case "csv":
		cw := csv.NewWriter(w)
		for _, r := range rows {
			if err := cw.Write([]string{r.SKU, strconv.Itoa(r.Units)}); err != nil {
				return err
			}
		}
		cw.Flush()
		return cw.Error()
	case "json":
		return json.NewEncoder(w).Encode(rows)
	default:
		return fmt.Errorf("unknown format %q", format)
	}
}

// --- Fix: export is closed for modification; formats extend it.

type Exporter interface {
	Export(w io.Writer, rows []Row) error
}

type CSVExporter struct{}

func (CSVExporter) Export(w io.Writer, rows []Row) error {
	cw := csv.NewWriter(w)
	for _, r := range rows {
		if err := cw.Write([]string{r.SKU, strconv.Itoa(r.Units)}); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

// ExporterFunc adapts a plain function, like http.HandlerFunc.
type ExporterFunc func(w io.Writer, rows []Row) error

func (f ExporterFunc) Export(w io.Writer, rows []Row) error { return f(w, rows) }

func export(w io.Writer, exporters map[string]Exporter, format string, rows []Row) error {
	e, ok := exporters[format]
	if !ok {
		return fmt.Errorf("unknown format %q", format)
	}
	return e.Export(w, rows)
}

func main() {
	// Wiring lives in main: adding "xml" means adding one entry here.
	exporters := map[string]Exporter{
		"csv": CSVExporter{},
		"json": ExporterFunc(func(w io.Writer, rows []Row) error {
			return json.NewEncoder(w).Encode(rows)
		}),
	}
	rows := []Row{{"KB-101", 4}, {"MS-220", 12}}
	for _, format := range []string{"csv", "json"} {
		var before, after bytes.Buffer
		if err := exportV1(&before, format, rows); err != nil {
			panic(err)
		}
		if err := export(&after, exporters, format, rows); err != nil {
			panic(err)
		}
		fmt.Printf("%s:\n%s", format, after.String())
		fmt.Println("same output:", before.String() == after.String())
	}
}
