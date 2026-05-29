/**
 * UI components renderer.
 * Converts API data models into interactive HTML/DOM elements.
 * Delegates specialized Canvas mapping and alert feeds to terrain_viz.js & detection_viz.js.
 */
const Components = {
  /**
   * Render SOP Profiles select options
   */
  renderSopProfileSelect(profiles, selectEl) {
    if (!selectEl) return;
    selectEl.innerHTML = '';
    
    profiles.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      selectEl.appendChild(opt);
    });
  },

  /**
   * Render sidebar mission summaries list
   */
  renderMissionSummaryList(summaries, activeId, containerEl, onClick) {
    if (!containerEl) return;
    containerEl.innerHTML = '';

    if (summaries.length === 0) {
      containerEl.innerHTML = `
        <div class="empty-state">
          <i data-lucide="layers-3"></i>
          <p>등록된 미션이 없습니다.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    summaries.forEach(m => {
      const card = document.createElement('div');
      card.className = `mission-card ${m.mission_id === activeId ? 'active' : ''} priority-${m.priority.toLowerCase()}`;
      
      const coveragePct = Math.round(m.map_coverage_ratio * 100);
      
      card.innerHTML = `
        <div class="mission-card-header">
          <span class="mission-id">${m.mission_id}</span>
          <span class="badge state-${m.status.toLowerCase()}">${m.status}</span>
        </div>
        <h4 class="mission-name">${m.name}</h4>
        <div class="mission-card-meta">
          <span><i data-lucide="alert-circle"></i> ${m.priority}</span>
          <span><i data-lucide="user"></i> ${m.sop_profile_id.split('_')[0]}</span>
        </div>
        <div class="mission-card-progress">
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${coveragePct}%"></div>
          </div>
          <div class="progress-stats">
            <span>지도 커버리지</span>
            <span>${coveragePct}%</span>
          </div>
        </div>
        ${m.victim_count > 0 ? `
          <div class="victim-alert-badge">
            <i data-lucide="activity" class="blink-icon"></i> 실종자 탐지 (${m.victim_count}명)
          </div>
        ` : ''}
      `;

      card.addEventListener('click', () => onClick(m.mission_id));
      containerEl.appendChild(card);
    });

    lucide.createIcons();
  },

  /**
   * Render main active mission panel details
   */
  renderMissionDetails(details, containerEl) {
    if (!containerEl) return;
    containerEl.innerHTML = '';

    const coveragePct = Math.round(details.map_coverage_ratio * 100);
    const dateStr = new Date(details.created_at_ms).toLocaleTimeString();

    // Serialize coordinates
    const coordsStr = details.search_area.coordinates
      .map(c => `(${c.x.toFixed(1)}, ${c.y.toFixed(1)})`)
      .join(' → ');

    // Render constraints list
    let constraintsHtml = '';
    if (details.sop_constraints && Object.keys(details.sop_constraints).length > 0) {
      constraintsHtml = Object.entries(details.sop_constraints)
        .map(([k, v]) => `
          <div class="constraint-item">
            <span class="constraint-key">${k}</span>
            <span class="constraint-val">${v}</span>
          </div>
        `).join('');
    } else {
      constraintsHtml = '<p class="no-data">추천된 SOP 제약조건이 없습니다.</p>';
    }

    // Determine Traversability Badge using TerrainVisualizer
    let traversabilityBadge = '';
    if (details.terrain_results.length > 0) {
      const latestTerrain = details.terrain_results[details.terrain_results.length - 1];
      traversabilityBadge = window.terrainVisualizer.getTraversabilityBadge(
        latestTerrain.traversability,
        latestTerrain.traversability_level
      );
    } else {
      traversabilityBadge = '<span class="safety-badge level-normal">STANDBY</span>';
    }

    containerEl.innerHTML = `
      <div class="details-section">
        <div class="details-row" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
          <div class="details-col">
            <label>미션 이름</label>
            <h3>${details.name}</h3>
          </div>
          <div class="details-col align-right" style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
            <span class="detail-val" style="font-size: 11px; color: var(--text-muted);">생성: ${dateStr}</span>
            ${traversabilityBadge}
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-title">로봇 이동 모드</span>
            <span class="stat-val locomotion-${details.robot_locomotion.toLowerCase()}">${details.robot_locomotion}</span>
          </div>
          <div class="stat-card">
            <span class="stat-title">현재 로봇 좌표</span>
            <span class="stat-val">X: ${details.current_pose.x.toFixed(1)}, Y: ${details.current_pose.y.toFixed(1)}</span>
          </div>
          <div class="stat-card">
            <span class="stat-title">경사각 / 거칠기</span>
            <span class="stat-val">${details.terrain_results.length > 0 ? `${details.terrain_results[details.terrain_results.length - 1].slope.toFixed(1)}° / ${details.terrain_results[details.terrain_results.length - 1].roughness.toFixed(2)}` : 'N/A'}</span>
          </div>
        </div>

        <div class="detail-block">
          <h4>탐색 경로 영역 (${details.search_area.area_type})</h4>
          <p class="coords-display"><i data-lucide="milestone"></i> ${coordsStr}</p>
        </div>

        <div class="detail-block">
          <h4>SOP 추천 제약조건</h4>
          <div class="constraints-grid">
            ${constraintsHtml}
          </div>
        </div>
      </div>
    `;

    lucide.createIcons();
  },

  /**
   * Render multi-sensor victim detection feed
   * Delegated to window.detectionVisualizer inside detection_viz.js
   */
  renderDetectionFeed(detections, containerEl) {
    if (!containerEl) return;
    containerEl.innerHTML = '';

    const activeDetections = detections.filter(d => d.detected);

    if (activeDetections.length === 0) {
      containerEl.innerHTML = `
        <div class="empty-feed">
          <i data-lucide="radar"></i>
          <p>탐색 중... 생존자가 발견되지 않았습니다.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    activeDetections.forEach((d, idx) => {
      // Delegate card generation to specialized visualizer
      const cardHtml = window.detectionVisualizer.renderDetectionCardHtml(d, idx);
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = cardHtml.trim();
      
      containerEl.appendChild(tempDiv.firstChild);
    });

    lucide.createIcons();
  },

  /**
   * Render domain events timeline logs
   */
  renderEventTimeline(events, containerEl) {
    if (!containerEl) return;
    containerEl.innerHTML = '';

    if (events.length === 0) {
      containerEl.innerHTML = `<p class="no-data">등록된 시스템 이벤트가 없습니다.</p>`;
      return;
    }

    // Show latest events first
    const sorted = [...events].reverse().slice(0, 15);

    sorted.forEach(e => {
      const item = document.createElement('div');
      item.className = `timeline-item type-${e.event_type.toLowerCase()}`;
      
      const timeStr = new Date(e.timestamp_ms).toLocaleTimeString();
      let icon = 'info';
      if (e.event_type.includes('STOP') || e.event_type.includes('FAILURE')) {
        icon = 'shield-alert';
      } else if (e.event_type.includes('CREATED') || e.event_type.includes('APPROVED')) {
        icon = 'clipboard-check';
      } else if (e.event_type.includes('ANALYZED')) {
        icon = 'binary';
      }

      item.innerHTML = `
        <div class="timeline-icon-wrap">
          <i data-lucide="${icon}"></i>
        </div>
        <div class="timeline-content">
          <div class="timeline-time">${timeStr}</div>
          <div class="timeline-type">${e.event_type}</div>
          <div class="timeline-desc">모듈: <strong>${e.source_module}</strong> | 대상: ${e.mission_id}</div>
        </div>
      `;

      containerEl.appendChild(item);
    });

    lucide.createIcons();
  },

  /**
   * Render dynamic 2D Robot Exploration and SLAM trajectory mapping on HTML Canvas
   * Delegated to window.terrainVisualizer inside terrain_viz.js
   */
  renderTerrainMapCanvas(canvasEl, details) {
    // Delegate to specialized terrain visualizer
    window.terrainVisualizer.drawTelemetryMap(canvasEl, details);
  }
};
