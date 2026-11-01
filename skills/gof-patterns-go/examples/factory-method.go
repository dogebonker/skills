package main

import (
	"fmt"
	"strings"
)

// Notifier is the product. Defined where it is consumed.
type Notifier interface {
	Send(to, body string) string
}

type emailNotifier struct{ from string }

func (e emailNotifier) Send(to, body string) string {
	return fmt.Sprintf("email from %s to %s: %s", e.from, to, body)
}

type smsNotifier struct{}

func (smsNotifier) Send(to, body string) string {
	return fmt.Sprintf("sms to %s: %.20s", to, body)
}

// NewNotifier is the factory method: callers name a kind, not a concrete type.
func NewNotifier(kind string) (Notifier, error) {
	switch kind {
	case "email":
		return emailNotifier{from: "noreply@example.com"}, nil
	case "sms":
		return smsNotifier{}, nil
	default:
		return nil, fmt.Errorf("unknown notifier kind %q", kind)
	}
}

func main() {
	for _, kind := range []string{"email", "sms", "pager"} {
		n, err := NewNotifier(kind)
		if err != nil {
			fmt.Println("error:", err)
			continue
		}
		fmt.Println(n.Send("alice", strings.Repeat("order shipped ", 3)))
	}
}
