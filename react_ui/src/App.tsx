import React, { useEffect } from 'react';
import { useStore } from './store/useStore';
import { TelemetryDashboard } from './components/TelemetryDashboard';
import { Terrain3DViewer } from './components/Terrain3DViewer';
import { MissionSetupPanel } from './components/MissionSetupPanel';
import { SOPPanel } from './components/SOPPanel';
import { Shield, Radio, Activity, Cpu } from 'lucide-react';

export const App: React.FC = () => {
  const { isConnected, connectWebSocket, updateTelemetry, addEvent, addVictim, telemetry } = useStore();

  // 1. Establish WebSocket Connection to Go Backend
  useEffect(() => {
    connectWebSocket();
  }, [connectWebSocket]);

  // 2. Offline Simulation Fallback Loop (Active only when WebSocket is offline)
  useEffect(() => {
    if (isConnected) return; // Disable simulation when Go server is online

    console.log("[UI Simulation] Running offline mock simulation loop...");

    const connTimeout = setTimeout(() => {
      addEvent({
        event_id: 'E-SYS-INIT',
        mission_id: 'M-INIT',
        robot_id: 'RESCUE_QUAD_01',
        event_type: 'MISSION_SETUP_APPLIED',
        timestamp_ms: Date.now(),
        source_module: 'SYSTEM_CORE',
        priority: 'NORMAL',
        payload: { status: 'STANDBY_READY' }
      });
    }, 1000);

    let angle = 0;
    const ticker = setInterval(() => {
      angle += 0.15;
      
      const r = 25;
      const nextX = parseFloat((Math.cos(angle) * r).toFixed(1));
      const nextY = parseFloat((Math.sin(angle) * r).toFixed(1));
      const nextTheta = parseFloat((angle % (2 * Math.PI)).toFixed(2));

      const batteryDrop = telemetry.batteryLevel > 15 ? 
        parseFloat((telemetry.batteryLevel - 0.05).toFixed(2)) : 94.0;

      const rawGas = 12 + Math.sin(angle * 2.5) * 6;
      const gasLevel = parseFloat((rawGas < 0 ? 1 : rawGas).toFixed(1));

      updateTelemetry({
        pose: { x: nextX, y: nextY, theta: nextTheta },
        batteryLevel: batteryDrop,
        gasLevel: gasLevel,
        status: 'SEARCHING'
      });

      if (Math.random() > 0.93) {
        const victimId = `V-${Math.floor(100 + Math.random() * 900)}`;
        const confidence = parseFloat((75 + Math.random() * 24).toFixed(1));
        const sensorOptions: ('THERMAL' | 'RGB' | 'AUDIO')[] = ['THERMAL', 'RGB', 'AUDIO'];
        const chosenSensor = sensorOptions[Math.floor(Math.random() * sensorOptions.length)];

        addVictim({
          id: victimId,
          x: nextX,
          y: nextY,
          confidence: confidence,
          sensorType: chosenSensor,
          status: 'UNRESOLVED',
          detectedAtMs: Date.now()
        });

        addEvent({
          event_id: `E-DET-${Math.floor(1000 + Math.random() * 9000)}`,
          mission_id: 'M-ACTIVE',
          robot_id: 'RESCUE_QUAD_01',
          event_type: chosenSensor === 'THERMAL' ? 'THERMAL_ALIVE' : chosenSensor === 'RGB' ? 'RGB_BODY_PART' : 'GAS_HAZARD',
          timestamp_ms: Date.now(),
          source_module: 'SENSORY_FUSION',
          priority: chosenSensor === 'THERMAL' ? 'CRITICAL' : 'HIGH',
          payload: { confidence, coords: { x: nextX, y: nextY } }
        });
      }
    }, 1200);

    return () => {
      clearTimeout(connTimeout);
      clearInterval(ticker);
    };
  }, [isConnected, updateTelemetry, addEvent, addVictim, telemetry.batteryLevel]);

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-base)', overflow: 'hidden' }}>
      
      {/* Control Center Header Navigation */}
      <header style={{ 
        height: '70px', 
        background: 'rgba(19, 27, 46, 0.85)', 
        borderBottom: '1px solid var(--border-glass)', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '0 24px',
        backdropFilter: 'blur(10px)',
        zIndex: 50
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0369a1 100%)', boxShadow: '0 0 15px rgba(6,182,212,0.3)' }}>
            <Shield size={20} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'var(--font-display)', letterSpacing: '0.5px' }}>
              POSTTECH <span style={{ color: 'var(--accent-cyan)' }}>RESCUE CONTROL CENTER</span>
            </h1>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              ROBOTIC MULTI-MODAL JOINT COMMAND HUB (Go/PostgreSQL/MinIO Edition)
            </div>
          </div>
        </div>

        {/* Live system monitoring bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', padding: '6px 12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '6px' }}>
            <Cpu size={14} color="var(--accent-amber)" />
            <span style={{ color: 'var(--text-secondary)' }}>COPROCESSOR:</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--accent-amber)' }}>ACTIVE (Go Core)</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', padding: '6px 12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '6px' }}>
            <Radio size={14} color="var(--accent-cyan)" />
            <span style={{ color: 'var(--text-secondary)' }}>TELEMETRY CH:</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--accent-cyan)' }}>WS://LOCALHOST:8080</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} color="var(--accent-emerald)" className="signal-animate" />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>HEALTH 100%</span>
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="dashboard-grid">
        {/* Left column: Setup and Mission Planning */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <MissionSetupPanel />
        </div>

        {/* Center column: Topography Radar (main canvas viewer) */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Terrain3DViewer />
        </div>

        {/* Right column: Robot Telemetries & SOP priorities */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%', overflowY: 'auto' }}>
          <div style={{ flex: '1.2' }}>
            <TelemetryDashboard />
          </div>
          <div style={{ flex: '1' }}>
            <SOPPanel />
          </div>
        </div>
      </main>
    </div>
  );
};
