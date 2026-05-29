package service

import (
	"fmt"
	"go_core/internal/config"
	"go_core/internal/domain"
)

// DecideDriveProfile implements the terrain-driven locomotion policy decision rules.
func DecideDriveProfile(
	terrain domain.TerrainAnalysisResult,
	method domain.SearchMethod,
	thresholds *config.TerrainThresholds,
) domain.SearchDriveProfile {
	t := thresholds
	if t == nil {
		t = &config.DefaultTerrainThresholds
	}

	// Rule 1: Below stop threshold
	if terrain.TraversabilityScore < t.StopThreshold {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeStopAndReplan,
			SpeedScale:     0.0,
			MinClearanceCm: 0.0,
			ReplanRequired: true,
			ScanDensity:    "HIGH",
			Reason:         fmt.Sprintf("traversability_score %f < stop_threshold %f", terrain.TraversabilityScore, t.StopThreshold),
		}
	}

	// Rule 2: Cliff or blocked
	if terrain.TerrainClass == domain.TerrainClassCliffOrDrop ||
		terrain.TraversabilityLevel == domain.TraversabilityLevelBlocked {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeStopAndReplan,
			SpeedScale:     0.0,
			MinClearanceCm: 0.0,
			ReplanRequired: true,
			ScanDensity:    "HIGH",
			Reason:         fmt.Sprintf("terrain=%s, level=%s", terrain.TerrainClass, terrain.TraversabilityLevel),
		}
	}

	// Rule 3: Steep slope
	if terrain.TerrainClass == domain.TerrainClassSteepSlope {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeSlowSafe,
			SpeedScale:     t.SlowSpeed / t.NormalSpeed,
			MinClearanceCm: 40.0,
			ReplanRequired: false,
			ScanDensity:    "HIGH",
			Reason:         "steep slope — slow safe mode",
		}
	}

	// Rule 4: Rough rubble
	if terrain.TerrainClass == domain.TerrainClassRoughRubble {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeObstacleClimb,
			SpeedScale:     t.CrawlSpeed / t.NormalSpeed,
			MinClearanceCm: 50.0,
			ReplanRequired: true,
			ScanDensity:    "HIGH",
			Reason:         "rough rubble — obstacle climb mode",
		}
	}

	// Rule 5: Narrow passage
	if terrain.TerrainClass == domain.TerrainClassNarrowPassage {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeEdgeFollow,
			SpeedScale:     t.SlowSpeed / t.NormalSpeed,
			MinClearanceCm: 20.0,
			ReplanRequired: false,
			ScanDensity:    "NORMAL",
			Reason:         "narrow passage — edge follow mode",
		}
	}

	// Rule 6: Obstacle dense
	if terrain.TerrainClass == domain.TerrainClassObstacleDense {
		return domain.SearchDriveProfile{
			SearchMethod:   method,
			LocomotionMode: domain.LocomotionModeSlowSafe,
			SpeedScale:     t.SlowSpeed / t.NormalSpeed,
			MinClearanceCm: 40.0,
			ReplanRequired: true,
			ScanDensity:    "HIGH",
			Reason:         "obstacle dense — slow safe with replan",
		}
	}

	// Rule 7: Flat or mild — normal wheel
	return domain.SearchDriveProfile{
		SearchMethod:   method,
		LocomotionMode: domain.LocomotionModeWheel,
		SpeedScale:     1.0,
		MinClearanceCm: 30.0,
		ReplanRequired: false,
		ScanDensity:    "NORMAL",
		Reason:         fmt.Sprintf("terrain=%s — normal wheel mode", terrain.TerrainClass),
	}
}
