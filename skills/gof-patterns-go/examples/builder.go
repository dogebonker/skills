package main

import (
	"fmt"
	"time"
)

type Server struct {
	addr    string
	timeout time.Duration
	tls     bool
	maxConn int
}

// Option is the functional-options form of a builder.
type Option func(*Server)

func WithTimeout(d time.Duration) Option { return func(s *Server) { s.timeout = d } }
func WithTLS() Option                    { return func(s *Server) { s.tls = true } }
func WithMaxConn(n int) Option           { return func(s *Server) { s.maxConn = n } }

func NewServer(addr string, opts ...Option) (*Server, error) {
	s := &Server{addr: addr, timeout: 30 * time.Second, maxConn: 100}
	for _, opt := range opts {
		opt(s)
	}
	if s.maxConn <= 0 {
		return nil, fmt.Errorf("maxConn must be positive, got %d", s.maxConn)
	}
	return s, nil
}

func main() {
	s, err := NewServer(":8080", WithTLS(), WithTimeout(5*time.Second))
	if err != nil {
		fmt.Println("error:", err)
		return
	}
	fmt.Printf("%+v\n", *s)

	_, err = NewServer(":8081", WithMaxConn(0))
	fmt.Println("error:", err)
}
