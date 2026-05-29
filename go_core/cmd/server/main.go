package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	pgAdapter "go_core/internal/adapters/postgres"
	storageAdapter "go_core/internal/adapters/storage"
	"go_core/internal/domain"
	"go_core/internal/ports"
	"go_core/internal/service"
)

var (
	upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow cross-origin connection from React UI (port 3000)
		},
	}

	// Active websocket connections
	clients = make(map[*websocket.Conn]bool)
)

func main() {
	// 1. Parse configuration
	port := getEnv("PORT", "8080")
	dbHost := getEnv("DB_HOST", "127.0.0.1")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "postgres")
	dbPass := getEnv("DB_PASSWORD", "secretpassword")
	dbName := getEnv("DB_NAME", "rescue_robot")
	dbSSL := getEnv("DB_SSLMODE", "disable")

	minioEndpoint := getEnv("MINIO_ENDPOINT", "127.0.0.1:9000")
	minioAccessKey := getEnv("MINIO_ACCESS_KEY", "minioadmin")
	minioSecretKey := getEnv("MINIO_SECRET_KEY", "minioadmin")
	minioUseSSLStr := getEnv("MINIO_USE_SSL", "false")
	minioUseSSL, _ := strconv.ParseBool(minioUseSSLStr)

	// 2. Initialize PostgreSQL connection
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=%s",
		dbHost, dbUser, dbPass, dbName, dbPort, dbSSL)
	
	log.Printf("Connecting to PostgreSQL at %s:%s...", dbHost, dbPort)
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	log.Println("PostgreSQL connection established successfully.")

	// Initialize repositories
	missionRepo := pgAdapter.NewPostgresMissionRepository(db)
	eventRepo := pgAdapter.NewPostgresEventRepository(db)

	// 3. Initialize MinIO connection
	log.Printf("Connecting to MinIO S3 storage at %s...", minioEndpoint)
	minioStorage, err := storageAdapter.NewMinIOAdapter(minioEndpoint, minioAccessKey, minioSecretKey, minioUseSSL)
	if err != nil {
		log.Fatalf("Failed to initialize MinIO storage adapter: %v", err)
	}
	log.Println("MinIO storage adapter initialized successfully.")

	// Pre-create standard default buckets
	ctx := context.Background()
	_ = minioStorage.UploadObject(ctx, "video", ".keep", nil, 0, "application/octet-stream")
	_ = minioStorage.UploadObject(ctx, "audio", ".keep", nil, 0, "application/octet-stream")
	_ = minioStorage.UploadObject(ctx, "maps", ".keep", nil, 0, "application/octet-stream")

	// 4. Initialize Core Logic Services
	safetyManager := service.NewSafetyManager()

	// 5. Setup Gin Web Server
	r := gin.Default()

	// CORS Middleware
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Setup API Routes
	api := r.Group("/api")
	{
		// Mission planning endpoints
		api.POST("/missions/draft", handleCreateDraft(missionRepo))
		api.POST("/missions/plan", handleApprovePlan(missionRepo))
		api.GET("/missions/drafts", handleListDrafts(missionRepo))
		api.GET("/missions/plans", handleListPlans(missionRepo))

		// Event logging endpoint
		api.POST("/events", handlePostEvent(eventRepo, safetyManager))

		// Media signed streaming URL endpoints
		api.GET("/media/presigned", handleGetPresignedURL(minioStorage))

		// System core status endpoint
		api.GET("/status", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"status":           "ONLINE",
				"safety_compliant": safetyManager.IsSafeToOperate(),
				"uptime_seconds":   time.Since(time.Now()).Seconds() * -1,
			})
		})

		// Live video frame broadcasting endpoint
		api.POST("/demo/send-frame", handleSendFrame())
	}

	// Live WebSockets telemetry endpoint
	r.GET("/ws/telemetry", func(c *gin.Context) {
		handleWebSocket(c.Writer, c.Request)
	})

	log.Printf("Control Center Backend starting on port %s...", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Server core failed: %v", err)
	}
}

// Handler functions for APIs

type DraftRequest struct {
	XMin         float64 `json:"XMin" binding:"required"`
	XMax         float64 `json:"XMax" binding:"required"`
	YMin         float64 `json:"YMin" binding:"required"`
	YMax         float64 `json:"YMax" binding:"required"`
	SearchMethod string  `json:"SearchMethod" binding:"required"`
}

func handleCreateDraft(repo ports.IMissionRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req DraftRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		missionID := fmt.Sprintf("M-%d", time.Now().UnixNano()/1e6)
		draft := domain.MissionDraft{
			MissionID: missionID,
			Request: domain.SearchMissionRequest{
				RequestID:    fmt.Sprintf("REQ-%s", missionID),
				OperatorID:   "COMMANDER_LEE",
				MissionName:  fmt.Sprintf("Mission %s", missionID),
				SearchArea:   domain.SearchArea{
					AreaType:    domain.SearchAreaTypePolygon,
					Coordinates: []domain.Pose3D{
						{X: req.XMin, Y: req.YMin, Z: 0},
						{X: req.XMax, Y: req.YMin, Z: 0},
						{X: req.XMax, Y: req.YMax, Z: 0},
						{X: req.XMin, Y: req.YMax, Z: 0},
					},
					FrameID: "map",
				},
				SearchMethod: domain.SearchMethod(req.SearchMethod),
				SOPProfileID: "SOP-DEFAULT",
				Priority:     domain.PriorityNormal,
				CreatedAtMs:  time.Now().UnixNano() / 1e6,
			},
			ValidationStatus: "PENDING_APPROVAL",
			SOPConstraints: map[string]interface{}{
				"MaxSlopeThreshold":      25.0,
				"GasSafetyGuardEnabled":  true,
				"AutonomousFailoverWiFi": "UNDER_20%",
			},
			DraftSnapshotID: fmt.Sprintf("SNAP-DRAFT-%d", time.Now().Unix()),
		}
		if err := repo.SaveDraft(draft); err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("failed to save draft: %v", err)})
			return
		}

		c.JSON(200, draft)
	}
}

type ConfirmPlanRequest struct {
	MissionID      string `json:"MissionID" binding:"required"`
	ApprovedBy     string `json:"ApprovedBy" binding:"required"`
	PlanSnapshotID string `json:"PlanSnapshotID" binding:"required"`
}

func handleApprovePlan(repo ports.IMissionRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req ConfirmPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		draft, err := repo.GetDraft(req.MissionID)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("failed to retrieve draft: %v", err)})
			return
		}
		if draft == nil {
			c.JSON(404, gin.H{"error": "mission draft not found"})
			return
		}

		plan, err := service.ApproveMission(*draft, req.ApprovedBy, time.Now().UnixNano()/1e6, req.PlanSnapshotID)
		if err != nil {
			c.JSON(400, gin.H{"error": fmt.Sprintf("failed approval guard: %v", err)})
			return
		}

		if err := repo.SavePlan(plan); err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("failed to persist plan: %v", err)})
			return
		}

		c.JSON(200, plan)
	}
}

func handleListDrafts(repo ports.IMissionRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		drafts, err := repo.ListDrafts()
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, drafts)
	}
}

func handleListPlans(repo ports.IMissionRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		plans, err := repo.ListPlans()
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, plans)
	}
}

func handlePostEvent(repo ports.IEventRepository, sm *service.SafetyManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		var event domain.BaseEvent
		if err := c.ShouldBindJSON(&event); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		event.TimestampMs = time.Now().UnixNano() / 1e6
		if event.EventID == "" {
			event.EventID = fmt.Sprintf("EV-%d", time.Now().UnixNano()/1e6)
		}

		// Apply GORM persistence
		if err := repo.SaveEvent(event); err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("failed to save event: %v", err)})
			return
		}

		// Apply safety manager compliance
		safetyState := sm.HandleEvent(event)

		// Broadcast event out to WebSockets client UI
		broadcastToWS(gin.H{
			"type":         "EVENT",
			"event":        event,
			"safety_state": safetyState,
		})

		c.JSON(200, gin.H{
			"status":       "EVENT_LOGGED",
			"safety_state": safetyState,
		})
	}
}

func handleGetPresignedURL(storage ports.IStorageAdapter) gin.HandlerFunc {
	return func(c *gin.Context) {
		bucket := c.Query("bucket")
		object := c.Query("object")

		if bucket == "" || object == "" {
			c.JSON(400, gin.H{"error": "bucket and object parameters are required"})
			return
		}

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		urlStr, err := storage.GetPresignedURL(ctx, bucket, object, 1*time.Hour)
		if err != nil {
			c.JSON(500, gin.H{"error": fmt.Sprintf("failed to sign URL: %v", err)})
			return
		}

		c.JSON(200, gin.H{"url": urlStr})
	}
}

// Websocket handler & broadcast

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Websocket upgrade failed: %v", err)
		return
	}
	defer conn.Close()

	clients[conn] = true
	log.Printf("React Control Panel UI connected via WebSocket. Active sessions: %d", len(clients))

	for {
		// Read messages (telemetries from robot simulator, or commands from UI)
		var msg map[string]interface{}
		err := conn.ReadJSON(&msg)
		if err != nil {
			log.Printf("WebSocket connection dropped: %v", err)
			delete(clients, conn)
			break
		}

		// Echo / Broadcast back for cross-client sync
		broadcastToWS(msg)
	}
}

func broadcastToWS(data interface{}) {
	for conn := range clients {
		err := conn.WriteJSON(data)
		if err != nil {
			log.Printf("WebSocket writing error: %v", err)
			conn.Close()
			delete(clients, conn)
		}
	}
}

// Helper getenv
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

// Live Video Broadcast structures & handlers

type VideoFramePayload struct {
	FrameData   string `json:"frame_data" binding:"required"`
	SensorType  string `json:"sensor_type" binding:"required"`
	TimestampMs int64  `json:"timestamp_ms"`
}

func handleSendFrame() gin.HandlerFunc {
	return func(c *gin.Context) {
		var payload VideoFramePayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		ts := payload.TimestampMs
		if ts == 0 {
			ts = time.Now().UnixNano() / 1e6
		}

		// Broadcast to all WebSocket clients (compatible with legacy structure)
		broadcastToWS(gin.H{
			"type":       "VIDEO_FRAME",
			"event_type": "video.frame",
			"data": gin.H{
				"frame_data":   payload.FrameData,
				"sensor_type":  payload.SensorType,
				"timestamp_ms": ts,
			},
		})

		c.JSON(200, gin.H{"status": "BROADCASTED"})
	}
}
