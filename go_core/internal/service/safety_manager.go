package service

import (
	"fmt"
	"sync"
	"go_core/internal/domain"
)

type SafetyLevel int

const (
	SafetyLevelNormal        SafetyLevel = 0
	SafetyLevelCaution       SafetyLevel = 1
	SafetyLevelSafeMode      SafetyLevel = 2
	SafetyLevelEmergencyStop SafetyLevel = 3
)

type SafetyState struct {
	Level                 SafetyLevel           `json:"level"`
	GasAlertActive        bool                  `json:"gas_alert_active"`
	EmergencyStopped      bool                  `json:"emergency_stopped"`
	Reason                string                `json:"reason"`
	RecommendedLocomotion domain.LocomotionMode `json:"recommended_locomotion"`
}

type SafetyManager struct {
	mu       sync.RWMutex
	state    SafetyState
	eventLog []domain.BaseEvent
}

func NewSafetyManager() *SafetyManager {
	return &SafetyManager{
		state: SafetyState{
			Level:                 SafetyLevelNormal,
			GasAlertActive:        false,
			EmergencyStopped:      false,
			Reason:                "",
			RecommendedLocomotion: domain.LocomotionModeWheel,
		},
	}
}

func (sm *SafetyManager) HandleEvent(event domain.BaseEvent) SafetyState {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	sm.eventLog = append(sm.eventLog, event)

	if event.EventType == domain.EventTypeEmergencyStop {
		sm.state = SafetyState{
			Level:                 SafetyLevelEmergencyStop,
			EmergencyStopped:      true,
			Reason:                fmt.Sprintf("Emergency stop: %s", event.EventID),
			RecommendedLocomotion: domain.LocomotionModeStopAndReplan,
		}
	} else if event.EventType == domain.EventTypeGasHazard {
		if !sm.state.EmergencyStopped {
			sm.state = SafetyState{
				Level:                 SafetyLevelSafeMode,
				GasAlertActive:        true,
				Reason:                fmt.Sprintf("Gas alert: %s", event.EventID),
				RecommendedLocomotion: domain.LocomotionModeStopAndReplan,
			}
		}
	} else if event.EventType == domain.EventTypeSlamFailure {
		if sm.state.Level < SafetyLevelSafeMode {
			sm.state = SafetyState{
				Level:                 SafetyLevelCaution,
				Reason:                fmt.Sprintf("SLAM failure: %s", event.EventID),
				RecommendedLocomotion: domain.LocomotionModeSlowSafe,
			}
		}
	} else if event.EventType == domain.EventTypeWebRTCDisconnected {
		if sm.state.Level < SafetyLevelSafeMode {
			sm.state = SafetyState{
				Level:                 SafetyLevelCaution,
				Reason:                fmt.Sprintf("Network disconnected: %s", event.EventID),
				RecommendedLocomotion: domain.LocomotionModeSlowSafe,
			}
		}
	}

	return sm.state
}

func (sm *SafetyManager) Reset() {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	if !sm.state.EmergencyStopped {
		sm.state = SafetyState{
			Level:                 SafetyLevelNormal,
			GasAlertActive:        false,
			EmergencyStopped:      false,
			Reason:                "",
			RecommendedLocomotion: domain.LocomotionModeWheel,
		}
	}
}

func (sm *SafetyManager) IsSafeToOperate() bool {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	return sm.state.Level <= SafetyLevelCaution
}

func (sm *SafetyManager) GetEventLog() []domain.BaseEvent {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	logCopy := make([]domain.BaseEvent, len(sm.eventLog))
	copy(logCopy, sm.eventLog)
	return logCopy
}
