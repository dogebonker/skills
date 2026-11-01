package main

import "fmt"

// Logger is what our code wants.
type Logger interface{ Log(msg string) }

// legacyAudit is a third-party type with a different shape.
type legacyAudit struct{}

func (legacyAudit) WriteEntry(level int, text string) {
	fmt.Printf("[audit L%d] %s\n", level, text)
}

// auditAdapter wraps the legacy type to satisfy Logger.
type auditAdapter struct{ a legacyAudit }

func (x auditAdapter) Log(msg string) { x.a.WriteEntry(2, msg) }

// LoggerFunc lets a plain function act as a Logger, an adapter for free.
type LoggerFunc func(string)

func (f LoggerFunc) Log(msg string) { f(msg) }

func process(l Logger) { l.Log("order 42 processed") }

func main() {
	process(auditAdapter{legacyAudit{}})
	process(LoggerFunc(func(s string) { fmt.Println("[func]", s) }))
}
