/**
 * Detection Sensor Fusion Visualization Engine.
 * Manages confidence gradients and sensor hierarchy indicators.
 */
class DetectionVisualizer {
  constructor() {
    // Sensor priority hierarchy specifications
    this.sensorWeights = {
      'THERMAL': { rank: 1, label: 'THERMAL (P1)' },
      'RGB': { rank: 2, label: 'RGB (P2)' },
      'AUDIO': { rank: 3, label: 'AUDIO (P3)' }
    };
  }

  /**
   * Generates dynamic linear color gradient based on confidence percentage
   */
  getConfidenceGradient(confidence) {
    const confPct = Math.round(confidence * 100);
    
    // Smooth transition: Green (Emerald) -> Yellow (Amber) -> Red (Rose)
    let hue = 140; // Default Emerald Green
    if (confidence < 0.9 && confidence >= 0.7) {
      hue = 40; // Amber Yellow
    } else if (confidence < 0.7) {
      hue = 350; // Rose Red
    }

    return `linear-gradient(90deg, hsl(${hue}, 75%, 50%) 0%, hsl(${hue}, 85%, 65%) ${confPct}%, rgba(255,255,255,0.04) ${confPct}%)`;
  }

  /**
   * Renders priority hierarchy badges matching (THERMAL > RGB > AUDIO) specifications
   */
  getSensorPriorityHtml(sensorType) {
    const weight = this.sensorWeights[sensorType] || { rank: 99, label: 'UNKNOWN' };
    let badgeClass = 'state-draft';
    
    if (weight.rank === 1) {
      badgeClass = 'state-emergency_stopped'; // Red glow
    } else if (weight.rank === 2) {
      badgeClass = 'state-approved';          // Blue glow
    } else if (weight.rank === 3) {
      badgeClass = 'state-active';            // Orange glow
    }

    return `<span class="badge ${badgeClass}">${weight.label}</span>`;
  }

  /**
   * Serializes a single fused victim decision into a sleek telemetry alert card
   */
  renderDetectionCardHtml(d, index) {
    const confPct = Math.round(d.confidence * 100);
    const gradient = this.getConfidenceGradient(d.confidence);
    const priorityBadge = this.getSensorPriorityHtml(d.primary_sensor);

    return `
      <div class="detection-alert-card confidence-${d.decision_level.toLowerCase()}">
        <div class="alert-pulse"></div>
        <div class="detection-info">
          <div class="detection-head">
            <span class="detection-title"><i data-lucide="alert-triangle"></i> 실종 생존자 감지 #${index + 1}</span>
            <div class="detection-badges">
              ${priorityBadge}
              <span class="badge confidence-badge">${d.decision_level}</span>
            </div>
          </div>
          <p class="detection-desc">
            주센서: <strong>${d.primary_sensor}</strong> | 판정: <strong>${d.label}</strong>
          </p>
          
          <!-- Gradient fill background track -->
          <div class="progress-bar-container mini" style="background: rgba(255,255,255,0.06); border-radius: 3px; height: 6px; overflow: hidden; margin: 8px 0 4px 0;">
            <div class="progress-bar-fill" style="width: 100%; height: 100%; background: ${gradient}; transition: all 0.4s ease;"></div>
          </div>
          
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-muted);">
            <span>신뢰 수준 계측</span>
            <span style="font-weight: 700; color: #fff;">${confPct}%</span>
          </div>
        </div>
      </div>
    `;
  }
}

// Global instance exposure
window.detectionVisualizer = new DetectionVisualizer();
