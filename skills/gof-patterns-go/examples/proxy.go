package main

import (
	"fmt"
	"sync"
)

type Fetcher interface{ Fetch(url string) string }

type httpFetcher struct{}

func (httpFetcher) Fetch(url string) string {
	fmt.Println("network call:", url)
	return "body of " + url
}

// cachingProxy has the same interface and controls access to the real one.
type cachingProxy struct {
	real Fetcher
	mu   sync.Mutex
	seen map[string]func() string
}

func newCachingProxy(real Fetcher) *cachingProxy {
	return &cachingProxy{real: real, seen: map[string]func() string{}}
}

func (p *cachingProxy) Fetch(url string) string {
	p.mu.Lock()
	get, ok := p.seen[url]
	if !ok {
		// One real fetch per URL, even under concurrency; the lock is held only to register it.
		get = sync.OnceValue(func() string { return p.real.Fetch(url) })
		p.seen[url] = get
	}
	p.mu.Unlock()
	return get()
}

func main() {
	var f Fetcher = newCachingProxy(httpFetcher{})
	fmt.Println(f.Fetch("https://example.com/a"))
	fmt.Println(f.Fetch("https://example.com/a"))

	var wg sync.WaitGroup
	// Four goroutines ask for the same URL: one network call.
	for range 4 {
		wg.Go(func() { f.Fetch("https://example.com/b") })
	}
	wg.Go(func() { f.Fetch("https://example.com/c") })
	wg.Wait()
}
