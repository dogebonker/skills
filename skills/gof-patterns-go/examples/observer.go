package main

import (
	"context"
	"fmt"
	"sync"
)

type PriceEvent struct {
	Symbol string
	Price  float64
}

// Subject fans events out to subscriber channels.
type Subject struct {
	mu   sync.Mutex
	subs []chan PriceEvent
}

// Subscribe returns a channel closed when ctx is cancelled.
func (s *Subject) Subscribe(ctx context.Context) <-chan PriceEvent {
	ch := make(chan PriceEvent, 8)
	s.mu.Lock()
	s.subs = append(s.subs, ch)
	s.mu.Unlock()
	context.AfterFunc(ctx, func() {
		s.mu.Lock()
		defer s.mu.Unlock()
		for i, c := range s.subs {
			if c == ch {
				s.subs = append(s.subs[:i], s.subs[i+1:]...)
				break
			}
		}
		close(ch)
	})
	return ch
}

func (s *Subject) Publish(e PriceEvent) {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, ch := range s.subs {
		select {
		case ch <- e:
		default: // slow subscriber: drop rather than block the publisher
		}
	}
}

func main() {
	var subj Subject
	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup
	for _, name := range []string{"ui", "alerts"} {
		ch := subj.Subscribe(ctx)
		wg.Add(1)
		go func() {
			defer wg.Done()
			for e := range ch {
				fmt.Printf("%s got %s=%.2f\n", name, e.Symbol, e.Price)
			}
		}()
	}
	subj.Publish(PriceEvent{"ACME", 12.5})
	// Closing a buffered channel still delivers queued events.
	cancel()
	wg.Wait()
}
