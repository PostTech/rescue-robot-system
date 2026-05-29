package ports

import "go_core/internal/domain"

type IMissionRepository interface {
	SaveDraft(draft domain.MissionDraft) error
	SavePlan(plan domain.SearchMissionPlan) error
	GetDraft(missionID string) (*domain.MissionDraft, error)
	GetPlan(missionID string) (*domain.SearchMissionPlan, error)
	ListDrafts() ([]domain.MissionDraft, error)
	ListPlans() ([]domain.SearchMissionPlan, error)
	Clear() error
}

type IEventRepository interface {
	SaveEvent(event domain.BaseEvent) error
	GetEvents(missionID string) ([]domain.BaseEvent, error)
	Clear() error
}
