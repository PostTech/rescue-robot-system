package config

type TerrainThresholds struct {
	MildSlopeMax     float64 `json:"mild_slope_max"`
	SteepSlopeMax    float64 `json:"steep_slope_max"`
	CliffSlopeMin    float64 `json:"cliff_slope_min"`
	PassableStepMax  float64 `json:"passable_step_max"`
	CautionStepMax   float64 `json:"caution_step_max"`
	BlockedStepMin   float64 `json:"blocked_step_min"`
	SmoothMax        float64 `json:"smooth_max"`
	ModerateMax      float64 `json:"moderate_max"`
	RoughMin         float64 `json:"rough_min"`
	SparseMax        float64 `json:"sparse_max"`
	DenseMin         float64 `json:"dense_min"`
	PassableMin      float64 `json:"passable_min"`
	CautionMin       float64 `json:"caution_min"`
	ReplanMin        float64 `json:"replan_min"`
	StopThreshold    float64 `json:"stop_threshold"`
	NormalSpeed      float64 `json:"normal_speed"`
	SlowSpeed        float64 `json:"slow_speed"`
	CrawlSpeed       float64 `json:"crawl_speed"`
}

var DefaultTerrainThresholds = TerrainThresholds{
	MildSlopeMax:     15.0,
	SteepSlopeMax:    35.0,
	CliffSlopeMin:    60.0,
	PassableStepMax:  10.0,
	CautionStepMax:   25.0,
	BlockedStepMin:   50.0,
	SmoothMax:        0.2,
	ModerateMax:      0.5,
	RoughMin:         0.7,
	SparseMax:        0.15,
	DenseMin:         0.5,
	PassableMin:      0.7,
	CautionMin:       0.4,
	ReplanMin:        0.2,
	StopThreshold:    0.1,
	NormalSpeed:      1.0,
	SlowSpeed:        0.3,
	CrawlSpeed:       0.1,
}
