import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { Send, CheckCircle, FileText, Settings, AlertTriangle } from 'lucide-react';
export const MissionSetupPanel: React.FC = () => {
  const { missionDraft, activePlan, setActivePlan, createDraftFromServer, approvePlanOnServer } = useStore();
  const [xmin, setXmin] = useState('-50');
  const [xmax, setXmax] = useState('50');
  const [ymin, setYmin] = useState('-50');
  const [ymax, setYmax] = useState('50');
  const [method, setMethod] = useState<'PARALLEL_SWEEP' | 'SPIRAL_SEARCH' | 'EXPANDING_SQUARE'>('PARALLEL_SWEEP');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Trigger Go Core Backend API to generate draft
  const handleGenerateDraft = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await createDraftFromServer(
        parseFloat(xmin),
        parseFloat(xmax),
        parseFloat(ymin),
        parseFloat(ymax),
        method
      );
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to connect to Go Core Backend. Please check if server is online.');
    } finally {
      setIsLoading(false);
    }
  };

  // Trigger Go Core Backend API to approve plan
  const handleApprovePlan = async () => {
    if (!missionDraft) return;
    setIsLoading(true);
    setError(null);
    try {
      const missionID = missionDraft.mission_id || missionDraft.MissionID;
      const snapshotID = missionDraft.draft_snapshot_id || missionDraft.DraftSnapshotID || `SNAP-${Date.now()}`;
      await approvePlanOnServer(missionID, "COMMANDER_LEE", `PLAN-${snapshotID}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to commit plan. Please check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%', overflowY: 'auto' }}>
      <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-display)' }}>
        <Settings size={20} color="var(--accent-amber)" /> MISSION PLANNING
      </h2>

      {/* Input Coordinates */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>SEARCH AREA GRID LIMITS (METERS)</span>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>X MIN</label>
            <input 
              type="number" 
              value={xmin}
              onChange={(e) => setXmin(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border-glass)', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', outline: 'none', fontFamily: 'var(--font-mono)' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>X MAX</label>
            <input 
              type="number" 
              value={xmax}
              onChange={(e) => setXmax(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border-glass)', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', outline: 'none', fontFamily: 'var(--font-mono)' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Y MIN</label>
            <input 
              type="number" 
              value={ymin}
              onChange={(e) => setYmin(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border-glass)', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', outline: 'none', fontFamily: 'var(--font-mono)' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Y MAX</label>
            <input 
              type="number" 
              value={ymax}
              onChange={(e) => setYmax(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border-glass)', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', outline: 'none', fontFamily: 'var(--font-mono)' }}
            />
          </div>
        </div>
      </div>
      {/* Search algorithm */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>SWEEP & SEARCH METHOD</span>
        <select 
          value={method} 
          onChange={(e) => setMethod(e.target.value as any)}
          style={{ width: '100%', padding: '10px', border: '1px solid var(--border-glass)', borderRadius: '6px', background: 'rgba(19, 27, 46, 0.9)', color: 'var(--text-primary)', outline: 'none', cursor: 'pointer' }}
        >
          <option value="PARALLEL_SWEEP">PARALLEL SWEEP (Zigzag sweep)</option>
          <option value="SPIRAL_SEARCH">SPIRAL SEARCH (Spiral outward)</option>
          <option value="EXPANDING_SQUARE">EXPANDING SQUARE (Grid sweep)</option>
        </select>
      </div>

      {error && (
        <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--accent-red)', borderRadius: '6px', fontSize: '0.75rem', color: 'var(--accent-red)' }}>
          <strong>BACKEND CONNECT FAIL:</strong> {error}
        </div>
      )}

      <button
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, var(--accent-amber) 0%, #d97706 100%)',
          color: '#ffffff',
          fontWeight: 700,
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 4px 10px rgba(245, 158, 11, 0.2)',
          transition: 'var(--transition-smooth)',
          fontFamily: 'var(--font-display)'
        }}
        onClick={handleGenerateDraft}
        disabled={isLoading || !!activePlan}
      >
        <Send size={16} /> {isLoading ? 'PROCESSING DRAFT...' : 'GENERATE MISSION DRAFT'}
      </button>

      {/* Active plan status */}
      {activePlan && (
        <div style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.05)', border: '1px dashed var(--accent-emerald)', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.9rem' }}>
            <CheckCircle size={18} /> MISSION PLAN DEPLOYED
          </div>
          <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            <div>PLAN ID: {activePlan.MissionID}</div>
            <div>SWEEP: {activePlan.SearchMethod}</div>
            <div>SIGNATURE: {activePlan.ApprovedBy}</div>
          </div>
          <button 
            style={{ padding: '6px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)', background: 'transparent', color: 'var(--accent-red)', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, marginTop: '8px' }}
            onClick={() => setActivePlan(null)}
          >
            ABORT DEPLOYED PLAN
          </button>
        </div>
      )}

      {/* Show Draft Details waiting for approval */}
      {missionDraft && !activePlan && (
        <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.05)', border: '1px solid var(--accent-amber)', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-amber)', fontWeight: 700, fontSize: '0.85rem' }}>
            <FileText size={16} /> GO DRAFT: {missionDraft.MissionID}
          </div>
          
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px', fontFamily: 'var(--font-mono)' }}>
            <div>VALIDATION: <span style={{ color: 'var(--accent-emerald)' }}>{missionDraft.ValidationStatus}</span></div>
            <div>MAX SLOPE: {missionDraft.SOPConstraints.MaxSlopeThreshold}° Limit</div>
            <div>FORBIDDEN: {missionDraft.SOPConstraints.ForbiddenZones}</div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '10px' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px', fontWeight: 600 }}>
              <AlertTriangle size={12} /> AUTOMATED SOP GUARD WARNINGS
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>
              - WIFI Signal low retrace is ARMED.<br/>
              - High slope terrain profile is configured.
            </div>
          </div>

          <button
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              backgroundColor: 'var(--accent-emerald)',
              color: '#ffffff',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 10px rgba(16, 185, 129, 0.3)',
              transition: 'var(--transition-smooth)',
              fontFamily: 'var(--font-display)'
            }}
            onClick={handleApprovePlan}
          >
            COMMIT PLAN TO DATABASE
          </button>
        </div>
      )}
    </div>
  );
};
