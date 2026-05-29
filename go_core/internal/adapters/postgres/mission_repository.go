package postgres

import (
	"encoding/json"
	"go_core/internal/domain"
	"gorm.io/gorm"
)

type DraftModel struct {
	MissionID          string `gorm:"primaryKey"`
	RequestJSON        string `gorm:"type:text;not null"`
	ValidationStatus   string `gorm:"not null"`
	SOPConstraintsJSON string `gorm:"type:text;not null"`
	DraftSnapshotID    string `gorm:"not null"`
}

func (DraftModel) TableName() string {
	return "drafts"
}

type PlanModel struct {
	MissionID      string `gorm:"primaryKey"`
	SearchAreaJSON string `gorm:"type:text;not null"`
	SearchMethod   string `gorm:"not null"`
	ApprovedBy     string `gorm:"not null"`
	ApprovedAtMs   int64  `gorm:"not null"`
	PlanSnapshotID string `gorm:"not null"`
}

func (PlanModel) TableName() string {
	return "plans"
}

type PostgresMissionRepository struct {
	db *gorm.DB
}

func NewPostgresMissionRepository(db *gorm.DB) *PostgresMissionRepository {
	// Auto migrate GORM models
	_ = db.AutoMigrate(&DraftModel{}, &PlanModel{})
	return &PostgresMissionRepository{db: db}
}

func (r *PostgresMissionRepository) SaveDraft(draft domain.MissionDraft) error {
	reqBytes, err := json.Marshal(draft.Request)
	if err != nil {
		return err
	}

	sopBytes, err := json.Marshal(draft.SOPConstraints)
	if err != nil {
		return err
	}

	model := DraftModel{
		MissionID:          draft.MissionID,
		RequestJSON:        string(reqBytes),
		ValidationStatus:   draft.ValidationStatus,
		SOPConstraintsJSON: string(sopBytes),
		DraftSnapshotID:    draft.DraftSnapshotID,
	}

	return r.db.Save(&model).Error
}

func (r *PostgresMissionRepository) SavePlan(plan domain.SearchMissionPlan) error {
	areaBytes, err := json.Marshal(plan.SearchArea)
	if err != nil {
		return err
	}

	model := PlanModel{
		MissionID:      plan.MissionID,
		SearchAreaJSON: string(areaBytes),
		SearchMethod:   string(plan.SearchMethod),
		ApprovedBy:     plan.ApprovedBy,
		ApprovedAtMs:   plan.ApprovedAtMs,
		PlanSnapshotID: plan.PlanSnapshotID,
	}

	return r.db.Save(&model).Error
}

func (r *PostgresMissionRepository) GetDraft(missionID string) (*domain.MissionDraft, error) {
	var model DraftModel
	err := r.db.First(&model, "mission_id = ?", missionID).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, err
	}

	var req domain.SearchMissionRequest
	if err := json.Unmarshal([]byte(model.RequestJSON), &req); err != nil {
		return nil, err
	}

	var sop map[string]interface{}
	if err := json.Unmarshal([]byte(model.SOPConstraintsJSON), &sop); err != nil {
		return nil, err
	}

	return &domain.MissionDraft{
		MissionID:        model.MissionID,
		Request:          req,
		ValidationStatus: model.ValidationStatus,
		SOPConstraints:   sop,
		DraftSnapshotID:  model.DraftSnapshotID,
	}, nil
}

func (r *PostgresMissionRepository) GetPlan(missionID string) (*domain.SearchMissionPlan, error) {
	var model PlanModel
	err := r.db.First(&model, "mission_id = ?", missionID).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, err
	}

	var area domain.SearchArea
	if err := json.Unmarshal([]byte(model.SearchAreaJSON), &area); err != nil {
		return nil, err
	}

	return &domain.SearchMissionPlan{
		MissionID:      model.MissionID,
		SearchArea:     area,
		SearchMethod:   domain.SearchMethod(model.SearchMethod),
		ApprovedBy:     model.ApprovedBy,
		ApprovedAtMs:   model.ApprovedAtMs,
		PlanSnapshotID: model.PlanSnapshotID,
	}, nil
}

func (r *PostgresMissionRepository) ListDrafts() ([]domain.MissionDraft, error) {
	var models []DraftModel
	if err := r.db.Find(&models).Error; err != nil {
		return nil, err
	}

	var result []domain.MissionDraft
	for _, model := range models {
		var req domain.SearchMissionRequest
		_ = json.Unmarshal([]byte(model.RequestJSON), &req)
		var sop map[string]interface{}
		_ = json.Unmarshal([]byte(model.SOPConstraintsJSON), &sop)

		result = append(result, domain.MissionDraft{
			MissionID:        model.MissionID,
			Request:          req,
			ValidationStatus: model.ValidationStatus,
			SOPConstraints:   sop,
			DraftSnapshotID:  model.DraftSnapshotID,
		})
	}
	return result, nil
}

func (r *PostgresMissionRepository) ListPlans() ([]domain.SearchMissionPlan, error) {
	var models []PlanModel
	if err := r.db.Find(&models).Error; err != nil {
		return nil, err
	}

	var result []domain.SearchMissionPlan
	for _, model := range models {
		var area domain.SearchArea
		_ = json.Unmarshal([]byte(model.SearchAreaJSON), &area)

		result = append(result, domain.SearchMissionPlan{
			MissionID:      model.MissionID,
			SearchArea:     area,
			SearchMethod:   domain.SearchMethod(model.SearchMethod),
			ApprovedBy:     model.ApprovedBy,
			ApprovedAtMs:   model.ApprovedAtMs,
			PlanSnapshotID: model.PlanSnapshotID,
		})
	}
	return result, nil
}

func (r *PostgresMissionRepository) Clear() error {
	r.db.Session(&gorm.Session{AllowGlobalUpdate: true}).Delete(&DraftModel{})
	r.db.Session(&gorm.Session{AllowGlobalUpdate: true}).Delete(&PlanModel{})
	return nil
}
