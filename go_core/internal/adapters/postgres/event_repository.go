package postgres

import (
	"encoding/json"
	"go_core/internal/domain"
	"gorm.io/gorm"
)

type EventModel struct {
	EventID      string `gorm:"primaryKey"`
	MissionID    string `gorm:"index;not null"`
	RobotID      string `gorm:"not null"`
	EventType    string `gorm:"not null"`
	TimestampMs  int64  `gorm:"not null"`
	SourceModule string `gorm:"not null"`
	Priority     string `gorm:"not null"`
	PayloadJSON  string `gorm:"type:text;not null"`
}

func (EventModel) TableName() string {
	return "events"
}

type PostgresEventRepository struct {
	db *gorm.DB
}

func NewPostgresEventRepository(db *gorm.DB) *PostgresEventRepository {
	_ = db.AutoMigrate(&EventModel{})
	return &PostgresEventRepository{db: db}
}

func (r *PostgresEventRepository) SaveEvent(event domain.BaseEvent) error {
	payloadBytes, err := json.Marshal(event.Payload)
	if err != nil {
		return err
	}

	model := EventModel{
		EventID:      event.EventID,
		MissionID:    event.MissionID,
		RobotID:      event.RobotID,
		EventType:    string(event.EventType),
		TimestampMs:  event.TimestampMs,
		SourceModule: event.SourceModule,
		Priority:     string(event.Priority),
		PayloadJSON:  string(payloadBytes),
	}

	return r.db.Save(&model).Error
}

func (r *PostgresEventRepository) GetEvents(missionID string) ([]domain.BaseEvent, error) {
	var models []EventModel
	err := r.db.Where("mission_id = ?", missionID).Order("timestamp_ms asc").Find(&models).Error
	if err != nil {
		return nil, err
	}

	var result []domain.BaseEvent
	for _, model := range models {
		var payload map[string]interface{}
		_ = json.Unmarshal([]byte(model.PayloadJSON), &payload)

		result = append(result, domain.BaseEvent{
			EventID:      model.EventID,
			MissionID:    model.MissionID,
			RobotID:      model.RobotID,
			EventType:    domain.EventType(model.EventType),
			TimestampMs:  model.TimestampMs,
			SourceModule: model.SourceModule,
			Priority:     domain.EventPriority(model.Priority),
			Payload:      payload,
		})
	}
	return result, nil
}

func (r *PostgresEventRepository) Clear() error {
	r.db.Session(&gorm.Session{AllowGlobalUpdate: true}).Delete(&EventModel{})
	return nil
}
