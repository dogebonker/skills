package main

import "fmt"

// Implementation side: how a message is delivered.
type Sender interface{ Deliver(text string) }

type emailSender struct{}
type slackSender struct{}

func (emailSender) Deliver(t string) { fmt.Println("email:", t) }
func (slackSender) Deliver(t string) { fmt.Println("slack:", t) }

// Abstraction side: what kind of message. Holds a Sender, not a concrete one.
type Alert struct{ out Sender }

func (a Alert) Fire(service string) { a.out.Deliver("ALERT " + service + " is down") }

type Digest struct{ out Sender }

func (d Digest) Fire(items []string) { d.out.Deliver(fmt.Sprintf("digest: %d items", len(items))) }

func main() {
	// Two abstractions x two implementations, no 2x2 type explosion.
	for _, s := range []Sender{emailSender{}, slackSender{}} {
		Alert{s}.Fire("billing")
		Digest{s}.Fire([]string{"a", "b", "c"})
	}
}
