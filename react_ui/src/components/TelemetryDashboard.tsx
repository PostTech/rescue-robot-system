import React from 'react';
import { useStore } from '../store/useStore';
import { Battery, ShieldAlert, Wifi, Flame, Zap, Compass } from 'lucide-react';

export const TelemetryDashboard: React.FC = () => {
  const { telemetry, isConnected } = useStore();

  const getStatusColor = () => {
    switch (telemetry.status) {
      case 'EMERGENCY': return 'var(--accent-red)';
      case 'SEARCHING': return 'var(--accent-cyan)';
      case 'RETURNING': return 'var(--accent-amber)';
      default: return 'var(--accent-emerald)';
    }
  };

  const getGasSafetyStatus = () => {
    if (telemetry.gasLevel > 50) return { label: 'CRITICAL HAZARD', color: 'var(--accent-red)' };
    if (telemetry.gasLevel > 25) return { label: 'WARNING LEVEL', color: 'var(--accent-amber)' };
    return { label: 'SAFE ENVIRONMENT', color: 'var(--accent-emerald)' };
  };

  const gasStatus = getGasSafetyStatus();

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-display)' }}>
          <Zap size={20} color="var(--accent-cyan)" /> TELEMETRY DASHBOARD
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span 
            className="pulse-status" 
            style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: isConnected ? 'var(--accent-cyan)' : 'var(--accent-red)' 
            }} 
          />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: isConnected ? 'var(--accent-cyan)' : 'var(--accent-red)' }}>
            {isConnected ? 'LIVE CONNECTED' : 'OFFLINE SYNC'}
          </span>
        </div>
      </div>

      {/* Robot Profile */}
      <div style={{ padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ROBOT IDENTIFIER</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Compass size={16} color="var(--accent-cyan)" /> {telemetry.robotId}
        </div>
      </div>

      {/* Grid of indicators */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {/* Battery Card */}
        <div className="glass-panel" style={{ padding: '12px', background: 'rgba(255,255,255,0.01)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>BATTERY</span>
            <Battery size={16} color={telemetry.batteryLevel < 20 ? 'var(--accent-red)' : 'var(--accent-emerald)'} />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
            {telemetry.batteryLevel}%
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '6px', overflow: 'hidden' }}>
            <div style={{ 
              height: '100%', 
              width: `${telemetry.batteryLevel}%`, 
              backgroundColor: telemetry.batteryLevel < 20 ? 'var(--accent-red)' : 'var(--accent-emerald)',
              transition: 'width 0.5s ease-in-out'
            }} />
          </div>
        </div>

        {/* Signal Card */}
        <div className="glass-panel" style={{ padding: '12px', background: 'rgba(255,255,255,0.01)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>SIGNAL STRENGTH</span>
            <Wifi size={16} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
            {telemetry.wifiSignal}%
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--accent-cyan)', marginTop: '4px' }}>
            LTE/5G AUTONOMOUS RETRACE ENABLED
          </div>
        </div>
      </div>

      {/* Hazardous Gas Level Gauge */}
      <div className="glass-panel" style={{ padding: '16px', background: 'rgba(255,255,255,0.01)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
            <Flame size={14} color="var(--accent-red)" /> HAZARD GAS ACCUMULATION
          </span>
          <span style={{ fontSize: '0.75rem', color: gasStatus.color, fontWeight: 700 }}>
            {gasStatus.label}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '8px' }}>
          <span style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>{telemetry.gasLevel}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ppm</span>
        </div>
        <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
          <div style={{ 
            height: '100%', 
            width: `${Math.min(telemetry.gasLevel, 100)}%`, 
            background: `linear-gradient(to right, var(--accent-emerald) 0%, var(--accent-amber) 50%, var(--accent-red) 100%)`,
            transition: 'width 0.3s ease-in-out'
          }} />
        </div>
      </div>

      {/* System Operation Mode */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>NAVIGATION MODE</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={{ 
            flex: 1, 
            padding: '10px', 
            borderRadius: '6px', 
            border: '1px solid rgba(255,255,255,0.1)',
            background: telemetry.mode === 'AUTONOMOUS' ? 'var(--accent-cyan-glow)' : 'transparent',
            color: telemetry.mode === 'AUTONOMOUS' ? 'var(--text-primary)' : 'var(--text-secondary)',
            borderColor: telemetry.mode === 'AUTONOMOUS' ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'var(--transition-smooth)'
          }}>
            AUTONOMOUS
          </button>
          <button style={{ 
            flex: 1, 
            padding: '10px', 
            borderRadius: '6px', 
            border: '1px solid rgba(255,255,255,0.1)',
            background: telemetry.mode === 'TELEOP' ? 'var(--accent-amber-glow)' : 'transparent',
            color: telemetry.mode === 'TELEOP' ? 'var(--text-primary)' : 'var(--text-secondary)',
            borderColor: telemetry.mode === 'TELEOP' ? 'var(--accent-amber)' : 'rgba(255,255,255,0.1)',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'var(--transition-smooth)'
          }}>
            TELEOP (MANUAL)
          </button>
        </div>
      </div>

      {/* Safety Status Block */}
      <div style={{ 
        padding: '12px', 
        borderRadius: '8px', 
        backgroundColor: telemetry.status === 'EMERGENCY' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(16, 185, 129, 0.05)', 
        border: `1px solid ${telemetry.status === 'EMERGENCY' ? 'var(--accent-red)' : 'var(--accent-emerald)'}`,
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginTop: 'auto'
      }}>
        <ShieldAlert size={20} color={getStatusColor()} />
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>CURRENT OPERATING STATUS</div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: getStatusColor() }}>
            {telemetry.status} STATE
          </div>
        </div>
      </div>

      {/* Emergency Stop Button */}
      <button 
        style={{
          width: '100%',
          padding: '14px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)',
          color: '#ffffff',
          fontWeight: 800,
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-display)',
          letterSpacing: '1px',
          boxShadow: '0 4px 15px rgba(239, 68, 68, 0.4)',
          transition: 'var(--transition-smooth)'
        }}
        onClick={() => {
          alert("EMERGENCY PROTOCOL TRIGGERED. CUTTING ROBOT ACTUATOR POWER.");
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.filter = 'brightness(1.1)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 6px 20px rgba(239, 68, 68, 0.6)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.filter = 'brightness(1)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 15px rgba(239, 68, 68, 0.4)';
        }}
      >
        HARD STOP (EMERGENCY)
      </button>
    </div>
  );
};
