import { create } from 'zustand';

export interface Telemetry {
  robotId: string;
  batteryLevel: number;
  pose: { x: number; y: number; theta: number };
  gasLevel: number; // Gas Hazard density
  mode: 'TELEOP' | 'AUTONOMOUS';
  status: 'IDLE' | 'SEARCHING' | 'RETURNING' | 'EMERGENCY';
  wifiSignal: number; // dBm or percentage
}

export interface TerrainPoint {
  x: number;
  y: number;
  roughness: number;
  slope: number;
  obstacleDensity: number;
  driveProfile: string; // HIGH_SPEED, SAFE_TRAVERSE, STEP_CLIMB, CRITICAL_HALT
}

export interface Victim {
  id: string;
  x: number;
  y: number;
  confidence: number;
  sensorType: 'THERMAL' | 'RGB' | 'AUDIO';
  status: 'UNRESOLVED' | 'RESOLVING' | 'SECURED';
  detectedAtMs: number;
}

export interface BaseEvent {
  event_id: string;
  mission_id: string;
  robot_id: string;
  event_type: string;
  timestamp_ms: number;
  source_module: string;
  priority: 'CRITICAL' | 'HIGH' | 'NORMAL' | 'LOW';
  payload: any;
}

export const API_BASE = 'http://localhost:8080';
export const WS_BASE = 'ws://localhost:8080';

let wsReconnectTimeout: any = null;

interface ControlCenterState {
  // Connection state
  isConnected: boolean;
  setConnected: (status: boolean) => void;

  // Real-time telemetry
  telemetry: Telemetry;
  updateTelemetry: (tel: Partial<Telemetry>) => void;

  // Missions
  missionDraft: any | null;
  setMissionDraft: (draft: any) => void;
  activePlan: any | null;
  setActivePlan: (plan: any) => void;

  // Log events
  events: BaseEvent[];
  addEvent: (event: BaseEvent) => void;
  clearEvents: () => void;

  // Terrain map
  terrainGrid: TerrainPoint[];
  setTerrainGrid: (grid: TerrainPoint[]) => void;
  updateTerrainPoint: (point: TerrainPoint) => void;

  // Sensory Fusion Victims
  victims: Victim[];
  addVictim: (victim: Victim) => void;
  updateVictimStatus: (id: string, status: Victim['status']) => void;
  clearVictims: () => void;

  // Live video frame buffer
  liveFrame: string | null;
  setLiveFrame: (frame: string | null) => void;

  // Real REST & WS Server integrations
  createDraftFromServer: (xmin: number, xmax: number, ymin: number, ymax: number, method: string) => Promise<any>;
  approvePlanOnServer: (missionID: string, approvedBy: string, planSnapshotID: string) => Promise<any>;
  connectWebSocket: () => void;
}

export const useStore = create<ControlCenterState>((set, get) => ({
  isConnected: false,
  setConnected: (status) => set({ isConnected: status }),

  telemetry: {
    robotId: "RESCUE_QUAD_01",
    batteryLevel: 94,
    pose: { x: 0, y: 0, theta: 0 },
    gasLevel: 12.5,
    mode: 'AUTONOMOUS',
    status: 'IDLE',
    wifiSignal: 88,
  },
  updateTelemetry: (tel) => set((state) => ({ telemetry: { ...state.telemetry, ...tel } })),

  missionDraft: null,
  setMissionDraft: (draft) => set({ missionDraft: draft }),
  activePlan: null,
  setActivePlan: (plan) => set({ activePlan: plan }),

  events: [],
  addEvent: (event) => set((state) => ({ 
    events: [event, ...state.events].slice(0, 150) // Limit to 150 items
  })),
  clearEvents: () => set({ events: [] }),

  terrainGrid: [],
  setTerrainGrid: (grid) => set({ terrainGrid: grid }),
  updateTerrainPoint: (point) => set((state) => {
    const existingIndex = state.terrainGrid.findIndex(p => p.x === point.x && p.y === point.y);
    if (existingIndex > -1) {
      const newGrid = [...state.terrainGrid];
      newGrid[existingIndex] = point;
      return { terrainGrid: newGrid };
    }
    return { terrainGrid: [...state.terrainGrid, point] };
  }),

  victims: [],
  addVictim: (victim) => set((state) => {
    if (state.victims.some(v => v.id === victim.id)) return state;
    return { victims: [...state.victims, victim] };
  }),
  updateVictimStatus: (id, status) => set((state) => ({
    victims: state.victims.map(v => v.id === id ? { ...v, status } : v)
  })),
  clearVictims: () => set({ victims: [] }),

  liveFrame: null,
  setLiveFrame: (frame) => set({ liveFrame: frame }),

  // -------------------------------------------------------------------------
  // Server Integrations (REST & WebSocket)
  // -------------------------------------------------------------------------

  createDraftFromServer: async (xmin, xmax, ymin, ymax, method) => {
    try {
      const response = await fetch(`${API_BASE}/api/missions/draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          XMin: xmin,
          XMax: xmax,
          YMin: ymin,
          YMax: ymax,
          SearchMethod: method
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned error: ${response.statusText}`);
      }

      const draft = await response.json();
      set({ missionDraft: draft });
      
      // Auto add event to keep timeline reactive
      get().addEvent({
        event_id: `E-DRFT-${Date.now()}`,
        mission_id: draft.mission_id || draft.MissionID || 'M-DRAFT',
        robot_id: 'RESCUE_QUAD_01',
        event_type: 'MISSION_DRAFT_CREATED',
        timestamp_ms: Date.now(),
        source_module: 'CONTROL_CENTER_UI',
        priority: 'NORMAL',
        payload: { xmin, xmax, ymin, ymax, method }
      });

      return draft;
    } catch (error) {
      console.error("Failed to create mission draft on server:", error);
      throw error;
    }
  },

  approvePlanOnServer: async (missionID, approvedBy, planSnapshotID) => {
    try {
      const response = await fetch(`${API_BASE}/api/missions/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          MissionID: missionID,
          ApprovedBy: approvedBy,
          PlanSnapshotID: planSnapshotID
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned error: ${response.statusText}`);
      }

      const plan = await response.json();
      set({ activePlan: plan, missionDraft: null });

      // Auto add event to timeline
      get().addEvent({
        event_id: `E-PLAN-${Date.now()}`,
        mission_id: missionID,
        robot_id: 'RESCUE_QUAD_01',
        event_type: 'MISSION_PLAN_APPROVED',
        timestamp_ms: Date.now(),
        source_module: 'CONTROL_CENTER_UI',
        priority: 'HIGH',
        payload: { approvedBy, planSnapshotID }
      });

      return plan;
    } catch (error) {
      console.error("Failed to approve plan on server:", error);
      throw error;
    }
  },

  connectWebSocket: () => {
    if (wsReconnectTimeout) clearTimeout(wsReconnectTimeout);

    console.log(`Connecting to WebSocket: ${WS_BASE}/ws/telemetry`);
    const socket = new WebSocket(`${WS_BASE}/ws/telemetry`);

    socket.onopen = () => {
      console.log("WebSocket connected successfully to Go backend.");
      set({ isConnected: true });
    };

    socket.onclose = (event) => {
      console.warn("WebSocket connection closed. Reconnecting in 3 seconds...", event.reason);
      set({ isConnected: false });
      wsReconnectTimeout = setTimeout(() => {
        get().connectWebSocket();
      }, 3000);
    };

    socket.onerror = (error) => {
      console.error("WebSocket encountered an error:", error);
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        // Handle incoming live video frames from send_test_frame.py
        if (msg.event_type === 'video.frame' || msg.type === 'VIDEO_FRAME') {
          const data = msg.data || msg;
          set({ liveFrame: data.frame_data });
          return;
        }

        // Process message types broadcast by server
        if (msg.type === 'EVENT' && msg.event) {
          const ev = msg.event;
          get().addEvent({
            event_id: ev.event_id || ev.EventID || `E-WS-${Date.now()}`,
            mission_id: ev.mission_id || ev.MissionID || 'M-ACTIVE',
            robot_id: ev.robot_id || ev.RobotID || 'RESCUE_QUAD_01',
            event_type: ev.event_type || ev.EventType,
            timestamp_ms: ev.timestamp_ms || ev.TimestampMs || Date.now(),
            source_module: ev.source_module || ev.SourceModule,
            priority: ev.priority || ev.Priority || 'NORMAL',
            payload: ev.payload || ev.Payload
          });
        } else if (msg.type === 'TELEMETRY' && msg.telemetry) {
          get().updateTelemetry(msg.telemetry);
        } else if (msg.type === 'VICTIM' && msg.victim) {
          get().addVictim(msg.victim);
        } else {
          // Duck typing check for general direct message
          if (msg.pose) {
            get().updateTelemetry({
              pose: msg.pose,
              batteryLevel: msg.batteryLevel || msg.battery_level,
              gasLevel: msg.gasLevel || msg.gas_level,
              status: msg.status
            });
          }
          if (msg.event_id || msg.EventID) {
            get().addEvent({
              event_id: msg.event_id || msg.EventID,
              mission_id: msg.mission_id || msg.MissionID || '',
              robot_id: msg.robot_id || msg.RobotID || '',
              event_type: msg.event_type || msg.EventType || '',
              timestamp_ms: msg.timestamp_ms || msg.TimestampMs || Date.now(),
              source_module: msg.source_module || msg.SourceModule || '',
              priority: msg.priority || msg.Priority || 'NORMAL',
              payload: msg.payload || msg.Payload || {}
            });
          }
          if (msg.id && msg.sensorType) {
            get().addVictim(msg);
          }
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };
  }
}));

