package domain

type DetectionLabel string

const (
	DetectionLabelVictimAlive    DetectionLabel = "VICTIM_ALIVE"
	DetectionLabelVictimBodyPart DetectionLabel = "VICTIM_BODY_PART"
	DetectionLabelVictimAudio    DetectionLabel = "VICTIM_AUDIO"
	DetectionLabelNoDetection    DetectionLabel = "NO_DETECTION"
)

type DetectionResult struct {
	SensorType  string         `json:"sensor_type"`
	Label       DetectionLabel `json:"label"`
	Confidence  float64        `json:"confidence"`
	BoundingBox []float64      `json:"bounding_box"` // [x, y, w, h] or nil
	TimestampMs int64          `json:"timestamp_ms"`
}

type DecisionLevel string

const (
	DecisionLevelHigh   DecisionLevel = "HIGH"
	DecisionLevelMedium DecisionLevel = "MEDIUM"
	DecisionLevelLow    DecisionLevel = "LOW"
	DecisionLevelNone   DecisionLevel = "NONE"
)

type VictimDecision struct {
	Detected            bool              `json:"detected"`
	PrimarySensor       string            `json:"primary_sensor"`
	Label               DetectionLabel    `json:"label"`
	Confidence          float64           `json:"confidence"`
	DecisionLevel       DecisionLevel     `json:"decision_level"`
	ContributingResults []DetectionResult `json:"contributing_results"`
}
