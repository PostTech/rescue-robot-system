import React from 'react';
import { useStore } from '../store/useStore';
import { AlertTriangle, Bell, Flame, Camera, Volume2, Shield } from 'lucide-react';

export const SOPPanel: React.FC = () => {
  const { victims, events, liveFrame } = useStore();

  const [webrtcActive, setWebrtcActive] = React.useState(false);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const pcRef = React.useRef<RTCPeerConnection | null>(null);
  const wsRef = React.useRef<WebSocket | null>(null);

  React.useEffect(() => {
    let wsReconnectTimeout: any = null;

    const connectSignaling = () => {
      console.log("WebRTC: Connecting to signaling at ws://localhost:8080/ws/webrtc?role=receiver");
      const ws = new WebSocket("ws://localhost:8080/ws/webrtc?role=receiver");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebRTC: Signaling channel open. Dispatching 'ready' to sender...");
        ws.send(JSON.stringify({ type: "ready" }));
      };

      ws.onclose = () => {
        console.warn("WebRTC: Signaling channel closed. Retrying in 4 seconds...");
        setWebrtcActive(false);
        wsReconnectTimeout = setTimeout(connectSignaling, 4000);
      };

      ws.onerror = (err) => {
        console.error("WebRTC Signaling Error:", err);
      };

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === "offer") {
            console.log("WebRTC: SDP Offer received from sender. Negotiating E2E connection...");
            
            if (pcRef.current) {
              pcRef.current.close();
            }

            const pc = new RTCPeerConnection({
              iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
              ]
            });
            pcRef.current = pc;

            pc.oniceconnectionstatechange = () => {
              console.log("WebRTC ICE Connection State Changed:", pc.iceConnectionState);
              if (pc.iceConnectionState === "disconnected" || pc.iceConnectionState === "failed" || pc.iceConnectionState === "closed") {
                setWebrtcActive(false);
              }
            };

            pc.ontrack = (evt) => {
              console.log("WebRTC: Received video track!", evt.track, evt.streams);
              if (videoRef.current) {
                if (evt.streams && evt.streams[0]) {
                  videoRef.current.srcObject = evt.streams[0];
                } else {
                  console.log("WebRTC: Streams array empty, creating custom MediaStream from track.");
                  const newStream = new MediaStream();
                  newStream.addTrack(evt.track);
                  videoRef.current.srcObject = newStream;
                }
                setWebrtcActive(true);
              }
            };

            await pc.setRemoteDescription(new RTCSessionDescription(data));
            
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);

            await new Promise<void>((resolve) => {
              if (pc.iceGatheringState === 'complete') {
                resolve();
              } else {
                const checkState = () => {
                  if (pc.iceGatheringState === 'complete') {
                    pc.removeEventListener('icegatheringstatechange', checkState);
                    resolve();
                  }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
              }
            });

            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: "answer",
                sdp: pc.localDescription?.sdp
              }));
              console.log("WebRTC: SDP Answer successfully sent to sender.");
            }
          }
        } catch (err) {
          console.error("WebRTC: Failed to handle signaling packet:", err);
        }
      };
    };

    connectSignaling();

    return () => {
      if (wsReconnectTimeout) clearTimeout(wsReconnectTimeout);
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          try {
            wsRef.current.send(JSON.stringify({ type: "bye" }));
          } catch(e) {}
        }
        wsRef.current.close();
      }
      if (pcRef.current) {
        pcRef.current.close();
      }
    };
  }, []);

  const getSensorIcon = (type: string) => {
    switch (type) {
      case 'THERMAL':
        return <Flame size={14} color="var(--accent-red)" />;
      case 'RGB':
        return <Camera size={14} color="var(--accent-cyan)" />;
      case 'AUDIO':
        return <Volume2 size={14} color="var(--accent-amber)" />;
      default:
        return <Shield size={14} color="var(--text-muted)" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'var(--accent-red)';
      case 'HIGH':
        return 'var(--accent-amber)';
      case 'NORMAL':
        return 'var(--accent-cyan)';
      default:
        return 'var(--text-muted)';
    }
  };

  const displayVictims = victims.slice(-4).reverse();
  const displayEvents = events.slice(0, 15);

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
      {/* Live Video Feed Panel */}
      <div className="glass-panel" style={{ 
        padding: '12px', 
        background: 'rgba(0,0,0,0.2)', 
        border: '1px solid var(--border-glass)', 
        borderRadius: '8px',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span className="pulse-status" style={{ 
              width: '6px', 
              height: '6px', 
              borderRadius: '50%', 
              backgroundColor: webrtcActive ? 'var(--accent-cyan)' : liveFrame ? 'var(--accent-red)' : 'var(--text-muted)' 
            }} />
            {webrtcActive ? 'LIVE FEED (WEBRTC H.264)' : liveFrame ? 'LIVE FEED (THERMAL)' : 'STREAM STANDBY'}
          </span>
          <span style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: webrtcActive ? 'var(--accent-cyan)' : liveFrame ? 'var(--accent-red)' : 'var(--text-muted)' }}>
            {webrtcActive ? '30 FPS' : liveFrame ? '10 FPS' : 'NO SIGNAL'}
          </span>
        </div>
        
        <div style={{ 
          height: '160px', 
          backgroundColor: '#05070c', 
          borderRadius: '6px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
          border: '1px solid rgba(255,255,255,0.03)'
        }}>
          {/* WebRTC Video Stream */}
          <video 
            ref={videoRef}
            autoPlay 
            playsInline 
            muted
            style={{ 
              width: '100%', 
              height: '100%', 
              objectFit: 'cover',
              display: webrtcActive ? 'block' : 'none'
            }} 
          />

          {/* Legacy Base64 Fallback */}
          {!webrtcActive && liveFrame && (
            <img 
              src={`data:image/jpeg;base64,${liveFrame}`} 
              alt="Thermal Stream" 
              style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
            />
          )}

          {/* No Signal display */}
          {!webrtcActive && !liveFrame && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
              <Camera size={32} strokeWidth={1.5} />
              <span style={{ fontSize: '0.7rem', fontWeight: 500, letterSpacing: '0.5px' }}>WAITING FOR SENSOR INGESTION...</span>
            </div>
          )}
        </div>
      </div>

      {/* Sensor Priority Rule Alert Box */}
      <div style={{ padding: '12px', background: 'rgba(6, 182, 212, 0.05)', border: '1px solid var(--accent-cyan)', borderRadius: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
        <div style={{ fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
          <AlertTriangle size={14} color="var(--accent-cyan)" /> FUSION SENSOR PRIORITIZATION SPEC
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
          <span style={{ color: 'var(--accent-red)', fontWeight: 700 }}>1. THERMAL (Alive)</span>
          <span>➔</span>
          <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>2. RGB (Body Part)</span>
          <span>➔</span>
          <span style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>3. AUDIO (Voice)</span>
        </div>
      </div>

      {/* Identified Victims registry */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>IDENTIFIED VICTIM LOG</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {displayVictims.map((v) => (
            <div key={v.id} style={{ 
              padding: '10px', 
              borderRadius: '6px', 
              background: 'rgba(255,255,255,0.02)', 
              border: `1px solid ${v.status === 'SECURED' ? 'var(--accent-emerald)' : 'var(--border-glass)'}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {getSensorIcon(v.sensorType)} {v.id} <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>({v.sensorType})</span>
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  COORDINATES: X:{v.x}, Y:{v.y}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{v.confidence}%</span>
                <span style={{ 
                  fontSize: '0.6rem', 
                  padding: '2px 6px', 
                  borderRadius: '10px', 
                  fontWeight: 700,
                  backgroundColor: v.status === 'SECURED' ? 'var(--accent-emerald-glow)' : v.status === 'RESOLVING' ? 'var(--accent-amber-glow)' : 'var(--accent-red-glow)',
                  color: v.status === 'SECURED' ? 'var(--accent-emerald)' : v.status === 'RESOLVING' ? 'var(--accent-amber)' : 'var(--accent-red)',
                }}>
                  {v.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Incident Event Logs */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Bell size={14} color="var(--accent-cyan)" /> EVENT SYSTEM TELEMETRY
        </span>
        <div style={{ 
          maxHeight: '180px', 
          overflowY: 'auto', 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '6px',
          paddingRight: '4px'
        }}>
          {displayEvents.map(e => (
            <div key={e.event_id} style={{ 
              padding: '8px', 
              background: 'rgba(0,0,0,0.15)', 
              borderRadius: '4px', 
              fontSize: '0.7rem', 
              borderLeft: `3px solid ${getPriorityColor(e.priority)}` 
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{e.event_type}</span>
                <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{e.source_module}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>ID: {e.event_id}</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>{new Date(e.timestamp_ms).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
