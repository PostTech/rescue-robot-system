package domain

type PerceptionFrame struct {
	ThermalTemp      float64 `json:"thermal_temp"`
	RGBHumanDetected bool    `json:"rgb_human_detected"`
	RGBConfidence    float64 `json:"rgb_confidence"`
	AudioHelpDetected bool    `json:"audio_help_detected"`
	GasCO2           float64 `json:"gas_co2"`
	Slope            float64 `json:"slope"`
	ObstacleHeight   float64 `json:"obstacle_height"`
	WebRTCConnected  bool    `json:"webrtc_connected"`
	FiveGConnected   bool    `json:"fiveg_connected"`
}

type RescueDecision struct {
	VictimDetected       bool           `json:"victim_detected"`
	Reason               string         `json:"reason"`
	Confidence           float64        `json:"confidence"`
	Mode                 LocomotionMode `json:"mode"`
	LocalAutonomousMode  bool           `json:"local_autonomous_mode"`
	GasHazard            bool           `json:"gas_hazard"`
}
