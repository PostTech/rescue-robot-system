package service

import (
	"errors"
	"fmt"
	"go_core/internal/domain"
)

// ApproveMission enforces that a MissionDraft can only be approved if in PENDING_APPROVAL state.
func ApproveMission(
	draft domain.MissionDraft,
	approvedBy string,
	approvedAtMs int64,
	planSnapshotID string,
) (domain.SearchMissionPlan, error) {
	if draft.ValidationStatus != "PENDING_APPROVAL" {
		return domain.SearchMissionPlan{}, fmt.Errorf("cannot approve draft in status '%s'; expected 'PENDING_APPROVAL'", draft.ValidationStatus)
	}

	if approvedBy == "" {
		return domain.SearchMissionPlan{}, errors.New("approver operator ID cannot be empty")
	}

	return domain.SearchMissionPlan{
		MissionID:      draft.MissionID,
		SearchArea:     draft.Request.SearchArea,
		SearchMethod:   draft.Request.SearchMethod,
		ApprovedBy:     approvedBy,
		ApprovedAtMs:   approvedAtMs,
		PlanSnapshotID: planSnapshotID,
	}, nil
}
