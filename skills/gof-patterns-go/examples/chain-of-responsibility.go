package main

import (
	"errors"
	"fmt"
)

type Request struct {
	User   string
	Amount int
}

// Handler returns handled=true to stop the chain.
type Handler func(Request) (handled bool, err error)

func validate(r Request) (bool, error) {
	if r.Amount <= 0 {
		return true, errors.New("amount must be positive")
	}
	return false, nil
}

func autoApprove(r Request) (bool, error) {
	if r.Amount <= 100 {
		fmt.Println(r.User, "auto-approved")
		return true, nil
	}
	return false, nil
}

func manager(r Request) (bool, error) {
	if r.Amount <= 1000 {
		fmt.Println(r.User, "approved by manager")
		return true, nil
	}
	return false, nil
}

func run(r Request, chain ...Handler) error {
	for _, h := range chain {
		if handled, err := h(r); handled {
			return err
		}
	}
	return errors.New("no handler accepted the request")
}

func main() {
	chain := []Handler{validate, autoApprove, manager}
	for _, r := range []Request{{"ann", 50}, {"bob", 500}, {"cy", 5000}, {"di", -1}} {
		if err := run(r, chain...); err != nil {
			fmt.Println(r.User, "error:", err)
		}
	}
}
