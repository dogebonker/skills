package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
)

// Middleware wraps a handler and returns a handler of the same type.
type Middleware func(http.Handler) http.Handler

func logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("request:", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func requireToken(token string) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Header.Get("Authorization") != token {
				http.Error(w, "forbidden", http.StatusForbidden)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// chain applies middlewares so the first listed runs outermost.
func chain(h http.Handler, ms ...Middleware) http.Handler {
	for i := len(ms) - 1; i >= 0; i-- {
		h = ms[i](h)
	}
	return h
}

func main() {
	core := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "orders list")
	})
	h := chain(core, logging, requireToken("secret"))

	for _, tok := range []string{"", "secret"} {
		req := httptest.NewRequest("GET", "/orders", nil)
		req.Header.Set("Authorization", tok)
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, req)
		fmt.Println(rec.Code, rec.Body.String())
	}
}
