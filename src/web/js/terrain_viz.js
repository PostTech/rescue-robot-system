/**
 * Terrain Visualization Engine.
 * Manages exact HEX color mappings and traversability analytics rendering.
 */
class TerrainVisualizer {
  constructor() {
    // Exact color mapping required by step 19 specifications
    this.colorMap = {
      'FLAT_OPEN': '#4ade80',       // 초록 (Emerald Green)
      'MILD_SLOPE': '#a3e635',      // 연초록 (Lime Green)
      'STEEP_SLOPE': '#facc15',     // 노란 (Bright Yellow)
      'CLIFF_OR_DROP': '#ef4444',    // 빨강 (Vibrant Red)
      'ROUGH_RUBBLE': '#f97316',     // 주황 (Deep Orange)
      'OBSTACLE_DENSE': '#ec4899',   // 분홍 (Hot Pink)
      'NARROW_PASSAGE': '#8b5cf6',   // 보라 (Deep Purple)
      'UNKNOWN': '#64748b'           // 회색 (Slate Muted)
    };
  }

  /**
   * Returns exact required hex color code for a terrain classification
   */
  getTerrainColor(terrainClass) {
    return this.colorMap[terrainClass] || this.colorMap['UNKNOWN'];
  }

  /**
   * Map traversability score and levels to CSS badge classes
   */
  getTraversabilityBadge(score, level) {
    let badgeClass = 'level-normal';
    let label = 'PASSABLE';

    if (level === 'CAUTION' || (score < 0.8 && score >= 0.5)) {
      badgeClass = 'level-caution';
      label = 'CAUTION';
    } else if (level === 'BLOCKED' || score < 0.5) {
      badgeClass = 'level-emergency_stop';
      label = 'BLOCKED';
    }

    return `<span class="safety-badge ${badgeClass}">${label}</span>`;
  }

  /**
   * Refined 2D SLAM exploration and multi-terrain mapping onto HTML Canvas
   */
  drawTelemetryMap(canvasEl, details) {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    if (!ctx) return;

    const width = canvasEl.width;
    const height = canvasEl.height;

    // 1. Slate Background Grid
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = 'rgba(30, 41, 59, 0.5)';
    ctx.lineWidth = 1;
    const gridSize = 30;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const mapCoord = (val, maxDomain = 20) => {
      const ratio = (val + maxDomain) / (maxDomain * 2);
      return ratio * width;
    };

    // 2. Geofence area
    const polyCoords = details.search_area.coordinates;
    if (polyCoords && polyCoords.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
      ctx.fillStyle = 'rgba(56, 189, 248, 0.03)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);

      polyCoords.forEach((c, idx) => {
        const px = mapCoord(c.x);
        const py = mapCoord(-c.y);
        if (idx === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 3. Draw SLAM covered mapping trace
    if (details.map_coverage_ratio > 0) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)'; // Sky-blue explor path
      ctx.lineWidth = 5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      const maxTicks = Math.round(details.map_coverage_ratio * 100);
      for (let i = 0; i <= maxTicks; i++) {
        const progress = i / 100;
        const angle = progress * 4 * Math.PI;
        const radius = progress * 15.0;
        const tx = radius * Math.abs(angle % 2 - 1);
        const ty = radius * Math.abs((angle + 1.57) % 2 - 1);

        const px = mapCoord(tx);
        const py = mapCoord(-ty);

        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
    }

    // 4. Draw Ground Classification Mark points based on exact spec colors
    details.terrain_results.forEach((t, index) => {
      const progress = index / details.terrain_results.length;
      const angle = progress * details.map_coverage_ratio * 4 * Math.PI;
      const radius = progress * details.map_coverage_ratio * 15.0;
      const tx = radius * Math.abs(angle % 2 - 1);
      const ty = radius * Math.abs((angle + 1.57) % 2 - 1);
      
      const px = mapCoord(tx);
      const py = mapCoord(-ty);

      // Get exact HEX color mapping
      ctx.fillStyle = this.getTerrainColor(t.terrain_class);
      ctx.beginPath();
      ctx.arc(px, py, 6, 0, 2 * Math.PI);
      ctx.fill();

      // Soft glow
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // 5. Draw Robot Arrow (Rotates dynamically)
    const rx = mapCoord(details.current_pose.x);
    const ry = mapCoord(-details.current_pose.y);
    const ryaw = details.current_pose.yaw;

    ctx.save();
    ctx.translate(rx, ry);
    ctx.rotate(-ryaw);

    ctx.fillStyle = '#38bdf8';
    ctx.shadowBlur = 12;
    ctx.shadowColor = '#38bdf8';
    
    ctx.beginPath();
    ctx.moveTo(12, 0);
    ctx.lineTo(-8, -8);
    ctx.lineTo(-4, 0);
    ctx.lineTo(-8, 8);
    ctx.closePath();
    ctx.fill();
    
    ctx.restore();
  }
}

// Global instance exposure
window.terrainVisualizer = new TerrainVisualizer();
