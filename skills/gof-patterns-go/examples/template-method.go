package main

import "fmt"

// Steps is the varying part. Go has no inheritance, so the skeleton
// takes the steps as an interface instead of calling overridden methods.
type Steps interface {
	Read() []string
	Transform(string) string
	Write([]string)
}

// Run is the fixed algorithm (the template).
func Run(s Steps) {
	var out []string
	for _, line := range s.Read() {
		out = append(out, s.Transform(line))
	}
	s.Write(out)
}

type csvImport struct{}

func (csvImport) Read() []string            { return []string{"a,1", "b,2"} }
func (csvImport) Transform(l string) string { return "row<" + l + ">" }
func (csvImport) Write(rows []string)       { fmt.Println("csv ->", rows) }

// base supplies defaults; embed it to override only what differs.
type base struct{}

func (base) Transform(l string) string { return l }
func (base) Write(rows []string)       { fmt.Println("out ->", rows) }

type logImport struct{ base }

func (logImport) Read() []string { return []string{"ERROR disk", "INFO ok"} }

func main() {
	Run(csvImport{})
	Run(logImport{})
}
