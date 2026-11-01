package main

import (
	"fmt"
	"sync"
)

type Config struct{ Env string }

var (
	once     sync.Once
	instance *Config
)

// Get builds the Config exactly once, safely across goroutines.
// Usually a package-level var or an injected *Config is simpler and easier to test.
func Get() *Config {
	once.Do(func() {
		fmt.Println("loading config")
		instance = &Config{Env: "production"}
	})
	return instance
}

func main() {
	var wg sync.WaitGroup
	ptrs := make([]*Config, 5)
	for i := range ptrs {
		wg.Add(1)
		go func() {
			defer wg.Done()
			ptrs[i] = Get()
		}()
	}
	wg.Wait()
	same := true
	for _, p := range ptrs {
		same = same && p == ptrs[0]
	}
	fmt.Println("all same instance:", same, ptrs[0].Env)
}
