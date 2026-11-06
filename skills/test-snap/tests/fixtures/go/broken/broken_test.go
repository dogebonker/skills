package broken

import "testing"

func TestFine(t *testing.T) {}

func TestBroken(t *testing.T) {
	if true {
