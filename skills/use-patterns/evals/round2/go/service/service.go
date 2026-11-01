package service

import (
	"fmt"
	"strings"
)

const minPlateLen = 4

type Shop struct {
	Name       string
	HourlyRate float64
	CalloutFee float64
}

type Job struct {
	Plate string
	Hours float64
}

func (s Shop) Quote(job Job) float64 {
	return s.CalloutFee + job.Hours*s.HourlyRate
}

func (s Shop) WorkOrder(job Job) string {
	plate := normalizePlate(job.Plate)
	if plate == "" {
		return fmt.Sprintf("%s: rejected job without a valid plate", s.Name)
	}
	return fmt.Sprintf("%s: %s, %.1f h, %.2f EUR", s.Name, plate, job.Hours, s.Quote(job))
}

func normalizePlate(plate string) string {
	plate = strings.ToUpper(strings.TrimSpace(plate))
	if len(plate) < minPlateLen {
		return ""
	}
	return strings.ReplaceAll(plate, " ", "-")
}
