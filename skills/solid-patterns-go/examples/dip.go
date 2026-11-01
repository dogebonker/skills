// DIP in Go: the policy (signup) owns a small interface; the detail (the mail
// transport) satisfies it; main is the only place that names the concrete type.
package main

import (
	"fmt"
	"strings"
)

// consoleMailer stands in for an SMTP client in this demo.
type consoleMailer struct{ out *strings.Builder }

func (m consoleMailer) Send(to, subject string) error {
	fmt.Fprintf(m.out, "mail to=%s subject=%q\n", to, subject)
	return nil
}

var outbox strings.Builder

// --- Violation: the policy builds its own transport, so it imports and is
// tested through the low-level detail.

type SignupServiceV1 struct{ mailer consoleMailer }

func NewSignupServiceV1() *SignupServiceV1 {
	return &SignupServiceV1{mailer: consoleMailer{out: &outbox}}
}

func (s *SignupServiceV1) Register(email string) error {
	if !strings.Contains(email, "@") {
		return fmt.Errorf("invalid email %q", email)
	}
	return s.mailer.Send(email, "Welcome aboard")
}

// --- Fix: the abstraction is declared by, and belongs to, the policy side.

type Mailer interface {
	Send(to, subject string) error
}

type SignupService struct{ mailer Mailer }

// NewSignupService accepts an interface and returns a concrete *SignupService.
func NewSignupService(m Mailer) *SignupService { return &SignupService{mailer: m} }

func (s *SignupService) Register(email string) error {
	if !strings.Contains(email, "@") {
		return fmt.Errorf("invalid email %q", email)
	}
	return s.mailer.Send(email, "Welcome aboard")
}

func main() {
	emails := []string{"ana@example.com", "not-an-email"}

	for _, e := range emails {
		if err := NewSignupServiceV1().Register(e); err != nil {
			fmt.Fprintln(&outbox, "error:", err)
		}
	}
	before := outbox.String()

	var log strings.Builder
	svc := NewSignupService(consoleMailer{out: &log}) // the one place the detail is named
	for _, e := range emails {
		if err := svc.Register(e); err != nil {
			fmt.Fprintln(&log, "error:", err)
		}
	}
	fmt.Print(log.String())
	fmt.Println("same output:", before == log.String())
}
