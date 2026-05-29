import React, { useRef, useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { Eye, Maximize2 } from 'lucide-react';

export const Terrain3DViewer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { telemetry, terrainGrid } = useStore();
  const [rotation, setRotation] = useState(0.8); // Current isometric angle

  // Generate mock terrain grid if empty to show a beautiful initial topographic model
  const grid = terrainGrid.length > 0 ? terrainGrid : Array.from({ length: 11 }, (_, xi) => 
    Array.from({ length: 11 }, (_, yi) => {
      const x = (xi - 5) * 10;
      const y = (yi - 5) * 10;
      const roughness = Math.sin(xi / 2) * Math.cos(yi / 2) * 5 + 5;
      const slope = Math.sqrt(x*x + y*y) / 5;
      const obstacleDensity = (xi === 3 && yi === 4) || (xi === 7 && yi === 8) ? 80 : (xi % 3 === 0 ? 30 : 0);
      let driveProfile = 'SAFE_TRAVERSE';
      if (obstacleDensity > 70) driveProfile = 'CRITICAL_HALT';
      else if (slope > 18) driveProfile = 'STEP_CLIMB';
      else if (roughness > 6) driveProfile = 'HIGH_SPEED';

      return { x, y, roughness, slope, obstacleDensity, driveProfile };
    })
  ).flat();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let angle = rotation;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2 + 30;
      
      // Rotate grid slowly
      angle += 0.0015;
      
      // Draw Holographic Grid & Topographic lines
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.07)';
      ctx.lineWidth = 1;
      
      // Sort points for isometric rendering (Back-to-Front painter's algorithm)
      const sortedGrid = [...grid].sort((a, b) => {
        // Transform coordinates with angle to calculate depth
        const depthA = a.x * Math.sin(angle) + a.y * Math.cos(angle);
        const depthB = b.x * Math.sin(angle) + b.y * Math.cos(angle);
        return depthA - depthB;
      });

      // Isometric transformation helper
      const project = (x: number, y: number, z: number) => {
        // Scale down coordinates to fit canvas
        const scaleX = 22;
        const scaleY = 11;
        const scaleZ = 3.5;
        
        const rotX = x * Math.cos(angle) - y * Math.sin(angle);
        const rotY = x * Math.sin(angle) + y * Math.cos(angle);
        
        return {
          px: centerX + rotX * scaleX,
          py: centerY + rotY * scaleY - z * scaleZ
        };
      };

      // Draw ground axis projection
      ctx.beginPath();
      ctx.arc(centerX, centerY, 130, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.15)';
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw Grid Mesh
      sortedGrid.forEach((p) => {
        const elevation = (10 - p.roughness) + (p.obstacleDensity / 15);
        const { px, py } = project(p.x / 10, p.y / 10, elevation);

        // Grid nodes
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        
        // Node color based on obstacle & drive profile
        if (p.driveProfile === 'CRITICAL_HALT') {
          ctx.fillStyle = 'var(--accent-red)';
          ctx.shadowBlur = 10;
          ctx.shadowColor = 'var(--accent-red)';
        } else if (p.driveProfile === 'STEP_CLIMB') {
          ctx.fillStyle = 'var(--accent-amber)';
          ctx.shadowBlur = 0;
        } else {
          ctx.fillStyle = 'rgba(6, 182, 212, 0.4)';
          ctx.shadowBlur = 0;
        }
        ctx.fill();

        // Topographic wireframe mesh lines to right neighbors
        const rightNeighbor = grid.find(n => n.x === p.x + 10 && n.y === p.y);
        if (rightNeighbor) {
          const rElev = (10 - rightNeighbor.roughness) + (rightNeighbor.obstacleDensity / 15);
          const rProj = project(rightNeighbor.x / 10, rightNeighbor.y / 10, rElev);
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(rProj.px, rProj.py);
          ctx.strokeStyle = p.driveProfile === 'CRITICAL_HALT' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(6, 182, 212, 0.08)';
          ctx.stroke();
        }

        // Wireframe mesh lines to bottom neighbors
        const bottomNeighbor = grid.find(n => n.x === p.x && n.y === p.y + 10);
        if (bottomNeighbor) {
          const bElev = (10 - bottomNeighbor.roughness) + (bottomNeighbor.obstacleDensity / 15);
          const bProj = project(bottomNeighbor.x / 10, bottomNeighbor.y / 10, bElev);
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(bProj.px, bProj.py);
          ctx.strokeStyle = p.driveProfile === 'CRITICAL_HALT' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(6, 182, 212, 0.08)';
          ctx.stroke();
        }
      });

      // Render robot current position as a dynamic pulsing point
      const robZ = 6; // Mock robot elevation on top of grid
      const robProj = project(telemetry.pose.x / 10, telemetry.pose.y / 10, robZ);
      
      // Pulse ring
      ctx.beginPath();
      ctx.arc(robProj.px, robProj.py, 12 + Math.sin(Date.now() / 150) * 4, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Core robot indicator
      ctx.beginPath();
      ctx.arc(robProj.px, robProj.py, 6, 0, Math.PI * 2);
      ctx.fillStyle = 'var(--accent-cyan)';
      ctx.shadowBlur = 15;
      ctx.shadowColor = 'var(--accent-cyan)';
      ctx.fill();
      ctx.shadowBlur = 0; // reset

      // Legend overlay text directly in Canvas
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.font = '700 12px var(--font-display)';
      ctx.fillText("ACTIVE TOPOGRAPHY MAP [REALTIME]", 20, 35);
      
      // Mini crosshair center helper
      ctx.beginPath();
      ctx.moveTo(centerX - 10, centerY);
      ctx.lineTo(centerX + 10, centerY);
      ctx.moveTo(centerX, centerY - 10);
      ctx.lineTo(centerX, centerY + 10);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.stroke();

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [grid, telemetry.pose, rotation]);

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {/* Panel header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-display)' }}>
          <Eye size={20} color="var(--accent-cyan)" /> 3D HAZARD & SLOPE RADAR
        </h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            onClick={() => setRotation(r => r + 0.2)}
            style={{ padding: '6px', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem' }}
          >
            ROTATE VIEW
          </button>
          <Maximize2 size={16} style={{ color: 'var(--text-muted)', cursor: 'pointer' }} />
        </div>
      </div>

      {/* Isometric Canvas */}
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgba(0,0,0,0.18)', borderRadius: '8px', border: '1px solid var(--border-glass)', overflow: 'hidden' }}>
        <canvas 
          ref={canvasRef} 
          width={520} 
          height={320} 
          style={{ width: '100%', height: '100%', maxHeight: '350px' }} 
        />
      </div>

      {/* Legend & driveProfile status bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-cyan)' }} /> Active Robot Pose
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-red)' }} /> Critical Halt Zone
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-amber)' }} /> Step Climb Profile
        </span>
      </div>
    </div>
  );
};
