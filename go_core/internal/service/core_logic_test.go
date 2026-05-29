package service

import (
	"testing"
	"go_core/internal/config"
	"go_core/internal/domain"
)

func TestDecideDriveProfile(t *testing.T) {
	// 1. Flat open terrain should recommend WHEEL mode
	terrain := domain.TerrainAnalysisResult{
		TerrainClass:        domain.TerrainClassFlatOpen,
		SlopeDegree:         3.0,
		StepHeightCm:        1.0,
		RoughnessScore:      0.1,
		ObstacleDensity:     0.05,
		TraversabilityScore: 0.9,
		TraversabilityLevel: domain.TraversabilityLevelPassable,
		Traversable:         true,
	}

	profile := DecideDriveProfile(terrain, domain.SearchMethodParallelSweep, nil)
	if profile.LocomotionMode != domain.LocomotionModeWheel {
		t.Errorf("Expected WHEEL locomotion mode, got %s", profile.LocomotionMode)
	}
	if profile.SpeedScale != 1.0 {
		t.Errorf("Expected speed scale 1.0, got %f", profile.SpeedScale)
	}

	// 2. Cliff terrain should trigger STOP_AND_REPLAN
	cliff := domain.TerrainAnalysisResult{
		TerrainClass:        domain.TerrainClassCliffOrDrop,
		SlopeDegree:         75.0,
		TraversabilityScore: 0.05,
		TraversabilityLevel: domain.TraversabilityLevelBlocked,
	}
	profileCliff := DecideDriveProfile(cliff, domain.SearchMethodPerimeterSearch, nil)
	if profileCliff.LocomotionMode != domain.LocomotionModeStopAndReplan {
		t.Errorf("Expected STOP_AND_REPLAN for cliff, got %s", profileCliff.LocomotionMode)
	}
	if !profileCliff.ReplanRequired {
		t.Error("Replan should be required for cliffs")
	}

	// 3. Steep slope should trigger SLOW_SAFE mode
	steep := domain.TerrainAnalysisResult{
		TerrainClass:        domain.TerrainClassSteepSlope,
		SlopeDegree:         40.0,
		TraversabilityScore: 0.5,
		TraversabilityLevel: domain.TraversabilityLevelCaution,
	}
	profileSteep := DecideDriveProfile(steep, domain.SearchMethodContourSearch, nil)
	if profileSteep.LocomotionMode != domain.LocomotionModeSlowSafe {
		t.Errorf("Expected SLOW_SAFE for steep slope, got %s", profileSteep.LocomotionMode)
	}
	expectedSteepSpeed := config.DefaultTerrainThresholds.SlowSpeed / config.DefaultTerrainThresholds.NormalSpeed
	if profileSteep.SpeedScale != expectedSteepSpeed {
		t.Errorf("Expected speed scale %f, got %f", expectedSteepSpeed, profileSteep.SpeedScale)
	}
}

func TestFuseDetections(t *testing.T) {
	// 1. High confidence THERMAL victim alive should be selected as primary
	results := []domain.DetectionResult{
		{SensorType: "RGB", Label: domain.DetectionLabelVictimBodyPart, Confidence: 0.8, TimestampMs: 1000},
		{SensorType: "THERMAL", Label: domain.DetectionLabelVictimAlive, Confidence: 0.95, TimestampMs: 1000},
		{SensorType: "AUDIO", Label: domain.DetectionLabelVictimAudio, Confidence: 0.7, TimestampMs: 1000},
	}

	decision := FuseDetections(results, 0.5)
	if !decision.Detected {
		t.Error("Expected victim to be detected")
	}
	if decision.PrimarySensor != "THERMAL" {
		t.Errorf("Expected THERMAL to be primary sensor, got %s", decision.PrimarySensor)
	}
	if decision.Label != domain.DetectionLabelVictimAlive {
		t.Errorf("Expected VICTIM_ALIVE label, got %s", decision.Label)
	}
	if decision.DecisionLevel != domain.DecisionLevelHigh {
		t.Errorf("Expected HIGH decision level, got %s", decision.DecisionLevel)
	}

	// 2. Results below threshold should result in no detection
	resultsLow := []domain.DetectionResult{
		{SensorType: "THERMAL", Label: domain.DetectionLabelVictimAlive, Confidence: 0.2, TimestampMs: 1000},
	}
	decisionLow := FuseDetections(resultsLow, 0.5)
	if decisionLow.Detected {
		t.Error("Expected victim not to be detected due to low confidence")
	}
	if decisionLow.DecisionLevel != domain.DecisionLevelNone {
		t.Errorf("Expected NONE decision level, got %s", decisionLow.DecisionLevel)
	}
}

func TestApproveMission(t *testing.T) {
	draft := domain.MissionDraft{
		MissionID:        "M-001",
		ValidationStatus: "PENDING_APPROVAL",
		Request: domain.SearchMissionRequest{
			RequestID: "R-001",
			SearchArea: domain.SearchArea{
				AreaType: domain.SearchAreaTypePolygon,
				Coordinates: []domain.Pose3D{
					{X: 0.0, Y: 0.0, Z: 0.0},
				},
				FrameID: "map",
			},
			SearchMethod: domain.SearchMethodParallelSweep,
		},
	}

	plan, err := ApproveMission(draft, "COM-01", 1700000000, "SNAP-99")
	if err != nil {
		t.Fatalf("Expected no error on approval, got %v", err)
	}
	if plan.ApprovedBy != "COM-01" {
		t.Errorf("Expected approver COM-01, got %s", plan.ApprovedBy)
	}
	if plan.ApprovedAtMs != 1700000000 {
		t.Errorf("Expected timestamp 1700000000, got %d", plan.ApprovedAtMs)
	}

	// Approve non-pending draft should fail
	draft.ValidationStatus = "DRAFT"
	_, errDraft := ApproveMission(draft, "COM-01", 1700000000, "SNAP-99")
	if errDraft == nil {
		t.Error("Expected approval to fail for non-pending validation status")
	}
}

func TestSafetyManager(t *testing.T) {
	sm := NewSafetyManager()

	if !sm.IsSafeToOperate() {
		t.Error("Initial state should be safe to operate")
	}

	// 1. Send network disconnect event -> CAUTION state
	disconnectedEvent := domain.BaseEvent{
		EventID:      "E-001",
		EventType:    domain.EventTypeWebRTCDisconnected,
		SourceModule: "webrtc",
	}
	state := sm.HandleEvent(disconnectedEvent)
	if state.Level != SafetyLevelCaution {
		t.Errorf("Expected CAUTION level, got %d", state.Level)
	}
	if state.RecommendedLocomotion != domain.LocomotionModeSlowSafe {
		t.Errorf("Expected SLOW_SAFE recommended locomotion, got %s", state.RecommendedLocomotion)
	}

	// 2. Send Gas Hazard event -> SAFE_MODE state
	gasEvent := domain.BaseEvent{
		EventID:      "E-002",
		EventType:    domain.EventTypeGasHazard,
		SourceModule: "sensors",
	}
	stateGas := sm.HandleEvent(gasEvent)
	if stateGas.Level != SafetyLevelSafeMode {
		t.Errorf("Expected SAFE_MODE level, got %d", stateGas.Level)
	}
	if !stateGas.GasAlertActive {
		t.Error("Expected gas alert to be active")
	}
	if stateGas.RecommendedLocomotion != domain.LocomotionModeStopAndReplan {
		t.Errorf("Expected STOP_AND_REPLAN recommended locomotion, got %s", stateGas.RecommendedLocomotion)
	}

	// 3. Send Emergency Stop -> EMERGENCY_STOP state
	estopEvent := domain.BaseEvent{
		EventID:      "E-003",
		EventType:    domain.EventTypeEmergencyStop,
		SourceModule: "ui",
	}
	stateEstop := sm.HandleEvent(estopEvent)
	if stateEstop.Level != SafetyLevelEmergencyStop {
		t.Errorf("Expected EMERGENCY_STOP level, got %d", stateEstop.Level)
	}
	if !stateEstop.EmergencyStopped {
		t.Error("Expected emergency_stopped to be true")
	}

	// 4. Reset shouldn't work if emergency stopped
	sm.Reset()
	if sm.state.Level != SafetyLevelEmergencyStop {
		t.Error("Reset should have no effect when emergency stopped")
	}
}
