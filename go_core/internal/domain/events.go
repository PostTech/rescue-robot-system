package domain

type EventPriority string

const (
	EventPriorityCritical EventPriority = "CRITICAL"
	EventPriorityHigh     EventPriority = "HIGH"
	EventPriorityNormal   EventPriority = "NORMAL"
	EventPriorityLow      EventPriority = "LOW"
)

type EventType string

const (
	EventTypeThermalAlive             EventType = "THERMAL_ALIVE"
	EventTypeRGBBodyPart              EventType = "RGB_BODY_PART"
	EventTypeGasHazard                EventType = "GAS_HAZARD"
	EventTypeSlamFailure              EventType = "SLAM_FAILURE"
	EventTypeWebRTCDisconnected       EventType = "WEBRTC_DISCONNECTED"
	EventTypeEmergencyStop            EventType = "EMERGENCY_STOP"
	EventTypeSearchMissionCreated     EventType = "SEARCH_MISSION_CREATED"
	EventTypeSearchAreaUpdated        EventType = "SEARCH_AREA_UPDATED"
	EventTypeSearchMethodSelected      EventType = "SEARCH_METHOD_SELECTED"
	EventTypeMissionSetupApplied      EventType = "MISSION_SETUP_APPLIED"
	EventTypeMissionApprovalRequested EventType = "MISSION_APPROVAL_REQUESTED"
	EventTypeTerrainAnalyzed          EventType = "TERRAIN_ANALYZED"
	EventTypeSearchDriveProfileSelected EventType = "SEARCH_DRIVE_PROFILE_SELECTED"
)

type BaseEvent struct {
	EventID      string                 `json:"event_id"`
	MissionID    string                 `json:"mission_id"`
	RobotID      string                 `json:"robot_id"`
	EventType    EventType              `json:"event_type"`
	TimestampMs  int64                  `json:"timestamp_ms"`
	SourceModule string                 `json:"source_module"`
	Priority     EventPriority          `json:"priority"`
	Payload      map[string]interface{} `json:"payload"`
}
