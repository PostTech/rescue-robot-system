package domain

// ---------------------------------------------------------------------------
// Common Value Objects
// ---------------------------------------------------------------------------

type Pose3D struct {
	X     float64 `json:"x"`
	Y     float64 `json:"y"`
	Z     float64 `json:"z"`
	Roll  float64 `json:"roll"`
	Pitch float64 `json:"pitch"`
	Yaw   float64 `json:"yaw"`
}

type Priority string

const (
	PriorityCritical Priority = "CRITICAL"
	PriorityHigh     Priority = "HIGH"
	PriorityNormal   Priority = "NORMAL"
	PriorityLow      Priority = "LOW"
)

type CommunicationStatus struct {
	WebRTCConnected bool    `json:"webrtc_connected"`
	FiveGConnected  bool    `json:"fiveg_connected"`
	PacketLossRate  float64 `json:"packet_loss_rate"`
}

// ---------------------------------------------------------------------------
// Mission Types
// ---------------------------------------------------------------------------

type SearchAreaType string

const (
	SearchAreaTypePolygon       SearchAreaType = "POLYGON"
	SearchAreaTypeWaypointRoute SearchAreaType = "WAYPOINT_ROUTE"
	SearchAreaTypeGrid          SearchAreaType = "GRID"
	SearchAreaTypeGeofence      SearchAreaType = "GEOFENCE"
)

type SearchMethod string

const (
	SearchMethodAreaSweep           SearchMethod = "AREA_SWEEP"
	SearchMethodParallelSweep       SearchMethod = "PARALLEL_SWEEP"
	SearchMethodCreepingLine        SearchMethod = "CREEPING_LINE"
	SearchMethodExpandingSquare       SearchMethod = "EXPANDING_SQUARE"
	SearchMethodSectorSearch        SearchMethod = "SECTOR_SEARCH"
	SearchMethodTracklineSearch     SearchMethod = "TRACKLINE_SEARCH"
	SearchMethodContourSearch       SearchMethod = "CONTOUR_SEARCH"
	SearchMethodTrackSweep          SearchMethod = "TRACK_SWEEP"
	SearchMethodSingleFile          SearchMethod = "SINGLE_FILE"
	SearchMethodGridCoverage        SearchMethod = "GRID_COVERAGE"
	SearchMethodFrontierExploration SearchMethod = "FRONTIER_EXPLORATION"
	SearchMethodWaypointRoute       SearchMethod = "WAYPOINT_ROUTE"
	SearchMethodSpiralSearch        SearchMethod = "SPIRAL_SEARCH"
	SearchMethodPerimeterSearch     SearchMethod = "PERIMETER_SEARCH"
	SearchMethodManualAssisted      SearchMethod = "MANUAL_ASSISTED"
)

type MissionStatus string

const (
	MissionStatusDraft           MissionStatus = "DRAFT"
	MissionStatusValidating      MissionStatus = "VALIDATING"
	MissionStatusPendingApproval MissionStatus = "PENDING_APPROVAL"
	MissionStatusApproved        MissionStatus = "APPROVED"
	MissionStatusActive          MissionStatus = "ACTIVE"
	MissionStatusCompleted       MissionStatus = "COMPLETED"
	MissionStatusCancelled       MissionStatus = "CANCELLED"
)

type SearchArea struct {
	AreaType    SearchAreaType         `json:"area_type" validate:"required"`
	Coordinates []Pose3D               `json:"coordinates" validate:"required,min=1"`
	FrameID     string                 `json:"frame_id" validate:"required"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type SearchMissionRequest struct {
	RequestID     string       `json:"request_id" validate:"required"`
	OperatorID    string       `json:"operator_id" validate:"required"`
	MissionName   string       `json:"mission_name" validate:"required"`
	SearchArea    SearchArea   `json:"search_area" validate:"required"`
	SearchMethod  SearchMethod `json:"search_method" validate:"required"`
	SOPProfileID  string       `json:"sop_profile_id" validate:"required"`
	Priority      Priority     `json:"priority" validate:"required"`
	CreatedAtMs   int64        `json:"created_at_ms" validate:"required"`
}

type MissionDraft struct {
	MissionID        string                 `json:"mission_id"`
	Request          SearchMissionRequest   `json:"request"`
	ValidationStatus string                 `json:"validation_status"`
	SOPConstraints   map[string]interface{} `json:"sop_constraints"`
	DraftSnapshotID  string                 `json:"draft_snapshot_id"`
}

type SearchMissionPlan struct {
	MissionID      string       `json:"mission_id"`
	SearchArea     SearchArea   `json:"search_area"`
	SearchMethod   SearchMethod `json:"search_method"`
	ApprovedBy     string       `json:"approved_by"`
	ApprovedAtMs   int64        `json:"approved_at_ms"`
	PlanSnapshotID string       `json:"plan_snapshot_id"`
}

type MissionSetupRecommendation struct {
	RecommendedMethod   SearchMethod           `json:"recommended_method"`
	Constraints         map[string]interface{} `json:"constraints"`
	Warnings            []string               `json:"warnings"`
	RecommendationOnly  bool                   `json:"recommendation_only"`
}

type ControlCommandType string

const (
	ControlCommandTypeMove          ControlCommandType = "MOVE"
	ControlCommandTypeStop          ControlCommandType = "STOP"
	ControlCommandTypeEmergencyStop ControlCommandType = "EMERGENCY_STOP"
	ControlCommandTypeSetMode       ControlCommandType = "SET_MODE"
)

type ControlCommand struct {
	CommandID   string                 `json:"command_id"`
	MissionID   string                 `json:"mission_id"`
	RobotID     string                 `json:"robot_id"`
	CommandType ControlCommandType     `json:"command_type"`
	IssuedBy    string                 `json:"issued_by"`
	TimestampMs int64                  `json:"timestamp_ms"`
	Payload     map[string]interface{} `json:"payload"`
}

// ---------------------------------------------------------------------------
// Terrain Types
// ---------------------------------------------------------------------------

type TerrainClass string

const (
	TerrainClassFlatOpen      TerrainClass = "FLAT_OPEN"
	TerrainClassMildSlope     TerrainClass = "MILD_SLOPE"
	TerrainClassSteepSlope    TerrainClass = "STEEP_SLOPE"
	TerrainClassRoughRubble    TerrainClass = "ROUGH_RUBBLE"
	TerrainClassNarrowPassage TerrainClass = "NARROW_PASSAGE"
	TerrainClassObstacleDense TerrainClass = "OBSTACLE_DENSE"
	TerrainClassCliffOrDrop   TerrainClass = "CLIFF_OR_DROP"
	TerrainClassUnknown       TerrainClass = "UNKNOWN"
)

type TraversabilityLevel string

const (
	TraversabilityLevelPassable       TraversabilityLevel = "PASSABLE"
	TraversabilityLevelCaution        TraversabilityLevel = "CAUTION"
	TraversabilityLevelReplanRequired TraversabilityLevel = "REPLAN_REQUIRED"
	TraversabilityLevelBlocked        TraversabilityLevel = "BLOCKED"
)

type LocomotionMode string

const (
	LocomotionModeWheel         LocomotionMode = "WHEEL"
	LocomotionModeObstacleClimb LocomotionMode = "OBSTACLE_CLIMB"
	LocomotionModeSlowSafe      LocomotionMode = "SLOW_SAFE"
	LocomotionModeEdgeFollow    LocomotionMode = "EDGE_FOLLOW"
	LocomotionModeStopAndReplan LocomotionMode = "STOP_AND_REPLAN"
	LocomotionModeStop          LocomotionMode = "STOP"
)

type TerrainAnalysisResult struct {
	TerrainClass        TerrainClass        `json:"terrain_class" validate:"required"`
	SlopeDegree         float64             `json:"slope_degree"`
	StepHeightCm        float64             `json:"step_height_cm"`
	RoughnessScore      float64             `json:"roughness_score"`
	ObstacleDensity     float64             `json:"obstacle_density"`
	TraversabilityScore float64             `json:"traversability_score"`
	TraversabilityLevel TraversabilityLevel `json:"traversability_level" validate:"required"`
	Traversable         bool                `json:"traversable"`
}

type LocomotionDecision struct {
	TargetMode       LocomotionMode `json:"target_mode"`
	RecommendedSpeed float64        `json:"recommended_speed"`
	Reason           string         `json:"reason"`
}

type SearchDriveProfile struct {
	SearchMethod     SearchMethod   `json:"search_method"`
	LocomotionMode   LocomotionMode `json:"locomotion_mode"`
	SpeedScale       float64        `json:"speed_scale"`
	MinClearanceCm   float64        `json:"min_clearance_cm"`
	ReplanRequired   bool           `json:"replan_required"`
	ScanDensity      string         `json:"scan_density"`
	Reason           string         `json:"reason"`
}

// ---------------------------------------------------------------------------
// Validation Types
// ---------------------------------------------------------------------------

type ValidationError struct {
	Field   string `json:"field"`
	Code    string `json:"code"`
	Message string `json:"message"`
}

type ValidationResult struct {
	IsValid bool              `json:"is_valid"`
	Errors  []ValidationError `json:"errors"`
}
