import React from 'react';
import { useStore } from '../store/useStore';
import { AlertTriangle, Bell, Flame, Camera, Volume2, Shield } from 'lucide-react';

export const SOPPanel: React.FC = () => {
  const { victims, events, liveFrame } = useStore();

  const [webrtcActive, setWebrtcActive] = React.useState(false);
  const [mediaStream, setMediaStream] = React.useState<MediaStream | null>(null);
  const [connStats, setConnStats] = React.useState({ connection: 'new', ice: 'new' });
  const [playbackStats, setPlaybackStats] = React.useState({ decoded: 0, dropped: 0, fps: 0 });
  const [trackState, setTrackState] = React.useState('none');
  const [delayStats, setDelayStats] = React.useState({ jitter: 0, decode: 0, total: 0, rtt: 0 });
  const [wsStatus, setWsStatus] = React.useState('DISCONNECTED');
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const pcRef = React.useRef<RTCPeerConnection | null>(null);
  const wsRef = React.useRef<WebSocket | null>(null);

  React.useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (mediaStream) {
      const tracks = mediaStream.getTracks();
      console.log(`[VIDEO-DBG] Assigning MediaStream (${tracks.length} tracks) to <video>`);
      tracks.forEach(t => console.log(`  Track: kind=${t.kind} readyState=${t.readyState} id=${t.id}`));

      video.srcObject = mediaStream;

      // Explicit play() — autoPlay alone is unreliable for dynamic srcObject
      const playPromise = video.play();
      if (playPromise) {
        playPromise.then(() => {
          console.log('[VIDEO-DBG] ✓ video.play() succeeded');
        }).catch((e: any) => {
          console.error('[VIDEO-DBG] ✗ video.play() FAILED:', e.name, e.message);
        });
      }
    } else {
      video.srcObject = null;
    }
  }, [mediaStream]);

  // Real-time Browser hardware H.264/VP8 frame decoder monitor
  React.useEffect(() => {
    if (!webrtcActive) {
      setPlaybackStats({ decoded: 0, dropped: 0, fps: 0 });
      return;
    }
    
    let lastDecoded = 0;
    const interval = setInterval(() => {
      if (videoRef.current) {
        // Query native browser video playback engine metrics
        const video = videoRef.current as any;
        if (video.getVideoPlaybackQuality) {
          const quality = video.getVideoPlaybackQuality();
          const decoded = quality.totalVideoFrames || 0;
          const dropped = quality.droppedVideoFrames || 0;
          const fps = decoded - lastDecoded;
          lastDecoded = decoded;
          setPlaybackStats({ decoded, dropped, fps: fps >= 0 ? fps : 0 });
        } else if (video.webkitDecodedFrameCount) {
          // Fallback for older Safari/WebKit engines
          const decoded = video.webkitDecodedFrameCount || 0;
          const dropped = video.webkitDroppedFrameCount || 0;
          const fps = decoded - lastDecoded;
          lastDecoded = decoded;
          setPlaybackStats({ decoded, dropped, fps: fps >= 0 ? fps : 0 });
        }
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [webrtcActive]);

  // WebRTC Stats API: E2E delay measurement
  React.useEffect(() => {
    if (!webrtcActive || !pcRef.current) return;

    const interval = setInterval(async () => {
      const pc = pcRef.current;
      if (!pc || pc.connectionState !== 'connected') return;

      try {
        const stats = await pc.getStats();
        stats.forEach((report: any) => {
          // Inbound RTP stats contain receiver-side delay metrics
          if (report.type === 'inbound-rtp' && report.kind === 'video') {
            const jitterBufferDelay = report.jitterBufferDelay || 0;       // total seconds in jitter buffer
            const jitterEmitted = report.jitterBufferEmittedCount || 1;    // frames emitted from buffer
            const totalDecodeTime = report.totalDecodeTime || 0;           // total seconds decoding
            const framesDecoded = report.framesDecoded || 1;
            const totalProcessingDelay = report.totalProcessingDelay || 0; // jitter + decode + render

            const avgJitterMs = (jitterBufferDelay / jitterEmitted) * 1000;
            const avgDecodeMs = (totalDecodeTime / framesDecoded) * 1000;
            const avgTotalMs = (totalProcessingDelay / jitterEmitted) * 1000;

            setDelayStats(prev => ({
              jitter: Math.round(avgJitterMs * 10) / 10,
              decode: Math.round(avgDecodeMs * 10) / 10,
              total: Math.round(avgTotalMs * 10) / 10,
              rtt: prev.rtt
            }));
          }
          // Candidate-pair stats contain RTT
          if (report.type === 'candidate-pair' && report.state === 'succeeded') {
            const rtt = (report.currentRoundTripTime || 0) * 1000;
            setDelayStats(prev => ({ ...prev, rtt: Math.round(rtt * 10) / 10 }));
          }
        });
      } catch (e) {
        // pc may have been closed
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [webrtcActive]);

  React.useEffect(() => {
    let wsReconnectTimeout: any = null;

    const connectSignaling = () => {
      console.log("WebRTC: Connecting to signaling at ws://127.0.0.1:8080/ws/webrtc?role=receiver");
      const ws = new WebSocket("ws://127.0.0.1:8080/ws/webrtc?role=receiver");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebRTC: Signaling channel open. Dispatching 'ready' to sender...");
        setWsStatus('CONNECTED → ready sent');
        ws.send(JSON.stringify({ type: "ready" }));
      };

      ws.onclose = (event: CloseEvent) => {
        if (event.code === 4001) {
          console.warn("WebRTC: Disconnected because another active tab opened. Disabling auto-reconnect to avoid session collision.");
          setWebrtcActive(false);
          setMediaStream(null);
          setWsStatus('BLOCKED (duplicate tab)');
          return;
        }
        console.warn("WebRTC: Signaling channel closed. Retrying in 4 seconds...");
        setWebrtcActive(false);
        setMediaStream(null);
        setWsStatus('CLOSED → retrying...');
        wsReconnectTimeout = setTimeout(connectSignaling, 4000);
      };

      ws.onerror = (err) => {
        console.error("WebRTC Signaling Error:", err);
        setWsStatus('ERROR (Go server down?)');
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
              iceServers: [] // Empty for instant offline local P2P negotiation (no STUN timeouts)
            });
            pcRef.current = pc;

            // Monitor state changes in real-time
            setConnStats({ connection: pc.connectionState, ice: pc.iceConnectionState });
            
            pc.onconnectionstatechange = () => {
              console.log("WebRTC Connection State Changed:", pc.connectionState);
              setConnStats(prev => ({ ...prev, connection: pc.connectionState }));
              if (pc.connectionState === "disconnected" || pc.connectionState === "failed" || pc.connectionState === "closed") {
                setWebrtcActive(false);
                setMediaStream(null);
              }
            };

            pc.oniceconnectionstatechange = () => {
              console.log("WebRTC ICE Connection State Changed:", pc.iceConnectionState);
              setConnStats(prev => ({ ...prev, ice: pc.iceConnectionState }));
              if (pc.iceConnectionState === "disconnected" || pc.iceConnectionState === "failed" || pc.iceConnectionState === "closed") {
                setWebrtcActive(false);
                setMediaStream(null);
              }
            };

            pc.ontrack = (evt) => {
              const t = evt.track;
              console.log(`[VIDEO-DBG] ontrack fired: kind=${t.kind} readyState=${t.readyState} id=${t.id}`);
              console.log(`[VIDEO-DBG] streams array length: ${evt.streams?.length}`);
              setTrackState(t.readyState);

              // Monitor track lifecycle
              t.onended = () => {
                console.warn('[VIDEO-DBG] Track ENDED');
                setTrackState('ended');
              };
              t.onmute = () => {
                console.warn('[VIDEO-DBG] Track MUTED');
                setTrackState('muted');
              };
              t.onunmute = () => {
                console.log('[VIDEO-DBG] Track UNMUTED (live)');
                setTrackState('live');
              };

              let stream: MediaStream;
              if (evt.streams && evt.streams[0]) {
                stream = evt.streams[0];
              } else {
                console.log('[VIDEO-DBG] Streams array empty, creating MediaStream from track.');
                stream = new MediaStream();
                stream.addTrack(t);
              }
              setMediaStream(stream);
              setWebrtcActive(true);
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
            {webrtcActive ? `${playbackStats.fps} FPS` : liveFrame ? '10 FPS' : 'NO SIGNAL'}
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
        {/* WebRTC Video Stream - ALWAYS in DOM (opacity controls visibility, NOT display) */}
          <video 
            ref={videoRef}
            autoPlay 
            playsInline 
            muted
            onLoadedMetadata={() => console.log('[VIDEO-DBG] ✓ loadedmetadata event')}
            onLoadedData={() => console.log('[VIDEO-DBG] ✓ loadeddata event - first frame decoded')}
            onPlaying={() => console.log('[VIDEO-DBG] ✓ playing event - video rendering started')}
            onStalled={() => console.warn('[VIDEO-DBG] ⚠ stalled event - no data arriving')}
            onWaiting={() => console.warn('[VIDEO-DBG] ⚠ waiting event - buffering')}
            onError={(e) => console.error('[VIDEO-DBG] ✗ error event:', (e.target as HTMLVideoElement).error)}
            style={{ 
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%', 
              height: '100%', 
              objectFit: 'cover',
              opacity: webrtcActive ? 1 : 0,
              zIndex: webrtcActive ? 2 : 0
            }} 
          />

          {/* Legacy Base64 Fallback (when WebRTC is not active but liveFrame exists) */}
          {!webrtcActive && liveFrame && (
            <img 
              src={`data:image/jpeg;base64,${liveFrame}`} 
              alt="Live thermal feed"
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'cover',
                position: 'absolute',
                top: 0,
                left: 0,
                zIndex: 1
              }} 
            />
          )}

          {/* No Signal Display */}
          {!webrtcActive && !liveFrame && (
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              justifyContent: 'center',
              gap: '6px',
              color: 'var(--text-muted)',
              fontSize: '0.7rem',
              fontFamily: 'var(--font-mono)',
              zIndex: 1
            }}>
              <Camera size={20} />
              <span>NO SIGNAL</span>
              <span style={{ 
                fontSize: '0.6rem', 
                padding: '2px 8px', 
                borderRadius: '4px',
                background: wsStatus.includes('CONNECTED') ? 'rgba(16,185,129,0.15)' : wsStatus.includes('ERROR') ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)',
                color: wsStatus.includes('CONNECTED') ? 'var(--accent-emerald)' : wsStatus.includes('ERROR') ? 'var(--accent-red)' : 'var(--accent-amber)',
                border: `1px solid ${wsStatus.includes('CONNECTED') ? 'rgba(16,185,129,0.3)' : wsStatus.includes('ERROR') ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`
              }}>
                WS: {wsStatus}
              </span>
              <span style={{ fontSize: '0.5rem', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.4 }}>
                {wsStatus.includes('ERROR') || wsStatus.includes('CLOSED') 
                  ? '① Go 서버(server_webrtc.exe)가 실행 중인지 확인'
                  : wsStatus.includes('CONNECTED') 
                    ? '② Python 송신기를 별도 터미널에서 실행:\npython send_video_file_webrtc.py'
                    : 'Go 서버 연결 대기 중...'}
              </span>
            </div>
          )}

          {/* WebRTC Real-time Diagnostic HUD Overlay */}
          {webrtcActive && (
            <div style={{
              position: 'absolute',
              top: '8px',
              left: '8px',
              background: 'rgba(5, 7, 12, 0.75)',
              backdropFilter: 'blur(4px)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              borderRadius: '4px',
              padding: '6px 8px',
              fontSize: '0.55rem',
              fontFamily: 'var(--font-mono)',
              color: 'var(--accent-cyan)',
              display: 'flex',
              flexDirection: 'column',
              gap: '2px',
              pointerEvents: 'none',
              zIndex: 10
            }}>
              <div style={{ fontWeight: 700, borderBottom: '1px solid rgba(6, 182, 212, 0.15)', paddingBottom: '2px', marginBottom: '2px', color: '#ffffff' }}>
                DIAGNOSTICS HUD
              </div>
              <div>CONN: <span style={{ color: connStats.connection === 'connected' ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>{connStats.connection.toUpperCase()}</span></div>
              <div>ICE: <span style={{ color: connStats.ice === 'connected' ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>{connStats.ice.toUpperCase()}</span></div>
              <div>DECODED: <span style={{ color: '#ffffff' }}>{playbackStats.decoded} frames</span></div>
              <div>DROPPED: <span style={{ color: playbackStats.dropped > 0 ? 'var(--accent-red)' : 'var(--text-muted)' }}>{playbackStats.dropped} frames</span></div>
              <div>LIVE FPS: <span style={{ color: playbackStats.fps > 0 ? 'var(--accent-cyan)' : 'var(--accent-red)', fontWeight: 800 }}>{playbackStats.fps} FPS</span></div>
              <div>TRACK: <span style={{ color: trackState === 'live' ? 'var(--accent-emerald)' : 'var(--accent-red)' }}>{trackState.toUpperCase()}</span></div>
              <div style={{ borderTop: '1px solid rgba(6, 182, 212, 0.15)', paddingTop: '2px', marginTop: '2px', fontWeight: 700, color: '#ffffff' }}>LATENCY</div>
              <div>RTT: <span style={{ color: 'var(--accent-cyan)' }}>{delayStats.rtt} ms</span></div>
              <div>JITTER BUF: <span style={{ color: delayStats.jitter > 100 ? 'var(--accent-red)' : 'var(--accent-emerald)' }}>{delayStats.jitter} ms</span></div>
              <div>DECODE: <span style={{ color: delayStats.decode > 30 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>{delayStats.decode} ms</span></div>
              <div>TOTAL: <span style={{ color: delayStats.total > 150 ? 'var(--accent-red)' : delayStats.total > 80 ? 'var(--accent-amber)' : 'var(--accent-emerald)', fontWeight: 800 }}>{delayStats.total} ms</span></div>
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
