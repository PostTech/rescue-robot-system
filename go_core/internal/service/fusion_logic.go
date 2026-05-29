package service

import (
	"sort"
	"go_core/internal/domain"
)

var SensorPriority = []string{"THERMAL", "RGB", "AUDIO"}

func FuseDetections(
	results []domain.DetectionResult,
	confidenceThreshold float64,
) domain.VictimDecision {
	// 1. Filter results above confidenceThreshold with actual detection
	var valid []domain.DetectionResult
	for _, r := range results {
		if r.Confidence >= confidenceThreshold && r.Label != domain.DetectionLabelNoDetection {
			valid = append(valid, r)
		}
	}

	if len(valid) == 0 {
		return domain.VictimDecision{
			Detected:            false,
			PrimarySensor:       "",
			Label:               domain.DetectionLabelNoDetection,
			Confidence:          0.0,
			DecisionLevel:       domain.DecisionLevelNone,
			ContributingResults: results,
		}
	}

	// 2. Sort by sensor priority
	priorityMap := map[string]int{
		"THERMAL": 0,
		"RGB":     1,
		"AUDIO":   2,
	}

	sort.SliceStable(valid, func(i, j int) bool {
		pi, okI := priorityMap[valid[i].SensorType]
		if !okI {
			pi = 99
		}
		pj, okJ := priorityMap[valid[j].SensorType]
		if !okJ {
			pj = 99
		}
		return pi < pj
	})

	primary := valid[0]

	// 3. Determine decision level
	var level domain.DecisionLevel
	if primary.Confidence >= 0.9 {
		level = domain.DecisionLevelHigh
	} else if primary.Confidence >= 0.7 {
		level = domain.DecisionLevelMedium
	} else {
		level = domain.DecisionLevelLow
	}

	return domain.VictimDecision{
		Detected:            true,
		PrimarySensor:       primary.SensorType,
		Label:               primary.Label,
		Confidence:          primary.Confidence,
		DecisionLevel:       level,
		ContributingResults: results,
	}
}
