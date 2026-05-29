/**
 * Main application logic.
 * Manages reactive UI state loops, event bindings, and simulated tick intervals.
 */
class App {
  constructor() {
    this.activeMissionId = null;
    this.autoTickInterval = null;
    this.refreshInterval = null;
  }

  async init() {
    console.log('Rescue Robot System Dashboard Initializing...');
    
    // Bind Action Buttons
    this.bindEvents();
    
    // Load initial SOP profiles
    await this.loadSopProfiles();
    
    // Initial fetch of missions
    await this.refreshMissionsList();

    // Start background refresh every 2.5 seconds
    this.refreshInterval = setInterval(() => {
      this.refreshMissionsList();
      this.updateSafetyStatus();
      this.updateEventTimeline();
    }, 2500);

    // Initial query for safety & events
    this.updateSafetyStatus();
    this.updateEventTimeline();
  }

  bindEvents() {
    // 1. Create Mission Form
    const createForm = document.getElementById('create-mission-form');
    if (createForm) {
      createForm.addEventListener('submit', (e) => this.handleCreateMission(e));
    }

    // 2. Control Action Buttons
    const btnApprove = document.getElementById('btn-approve');
    const btnStart = document.getElementById('btn-start');
    const btnComplete = document.getElementById('btn-complete');
    const btnStop = document.getElementById('btn-stop');
    const toggleTick = document.getElementById('toggle-auto-tick');

    if (btnApprove) btnApprove.addEventListener('click', () => this.handleApprove());
    if (btnStart) btnStart.addEventListener('click', () => this.handleStart());
    if (btnComplete) btnComplete.addEventListener('click', () => this.handleComplete());
    if (btnStop) btnStop.addEventListener('click', () => this.handleEmergencyStop());

    if (toggleTick) {
      toggleTick.addEventListener('change', (e) => this.handleToggleAutoTick(e.target.checked));
    }
  }

  // --- Load Initial SOP Metadata ---
  async loadSopProfiles() {
    try {
      const profiles = await window.apiClient.getSopProfiles();
      const selectEl = document.getElementById('mission-sop-profile');
      Components.renderSopProfileSelect(profiles, selectEl);
    } catch (err) {
      this.showToast('SOP 프로필 목록을 불러오지 못했습니다.', 'error');
    }
  }

  // --- Refresh Lists ---
  async refreshMissionsList() {
    try {
      const summaries = await window.apiClient.getMissions();
      const listEl = document.getElementById('missions-list-container');
      
      Components.renderMissionSummaryList(summaries, this.activeMissionId, listEl, (id) => {
        this.selectActiveMission(id);
      });

      // Auto-select first mission if none is active
      if (!this.activeMissionId && summaries.length > 0) {
        this.selectActiveMission(summaries[0].mission_id);
      }
    } catch (err) {
      console.error('Error refreshing missions:', err);
    }
  }

  async updateSafetyStatus() {
    try {
      const safety = await window.apiClient.getSafetyStatus();
      const levelEl = document.getElementById('safety-level-indicator');
      const textEl = document.getElementById('safety-text');
      const shellEl = document.getElementById('dashboard-shell');

      if (levelEl && textEl && shellEl) {
        levelEl.className = `safety-badge level-${safety.level.toLowerCase()}`;
        levelEl.textContent = safety.level;
        textEl.textContent = safety.reason || '로봇 시스템 정상 가동 중';

        // Red flashing background if emergency stopped
        if (safety.emergency_stopped) {
          shellEl.classList.add('emergency-alarm-active');
        } else {
          shellEl.classList.remove('emergency-alarm-active');
        }
      }
    } catch (err) {
      console.error('Error updating safety status:', err);
    }
  }

  async updateEventTimeline() {
    try {
      const events = await window.apiClient.getEvents();
      const listEl = document.getElementById('event-timeline-container');
      Components.renderEventTimeline(events, listEl);
    } catch (err) {
      console.error('Error updating timeline:', err);
    }
  }

  // --- Select Active Mission ---
  async selectActiveMission(missionId) {
    this.activeMissionId = missionId;
    
    // Highlight list
    this.refreshMissionsList();

    try {
      const details = await window.apiClient.getMissionDetails(missionId);
      
      // Render components
      Components.renderMissionDetails(details, document.getElementById('active-mission-details'));
      Components.renderDetectionFeed(details.detections, document.getElementById('detection-alerts-container'));
      
      const canvas = document.getElementById('terrain-canvas');
      Components.renderTerrainMapCanvas(canvas, details);

      // Enable/Disable Control Buttons based on state
      this.updateControlPanelButtons(details.status);
    } catch (err) {
      console.error('Error loading mission details:', err);
    }
  }

  updateControlPanelButtons(status) {
    const btnApprove = document.getElementById('btn-approve');
    const btnStart = document.getElementById('btn-start');
    const btnComplete = document.getElementById('btn-complete');
    const btnStop = document.getElementById('btn-stop');
    const tickWrapper = document.getElementById('tick-simulator-wrapper');

    // Reset all disabled states
    btnApprove.disabled = true;
    btnStart.disabled = true;
    btnComplete.disabled = true;
    btnStop.disabled = true;

    if (status === 'DRAFT') {
      btnApprove.disabled = false;
    } else if (status === 'APPROVED') {
      btnStart.disabled = false;
    } else if (status === 'ACTIVE') {
      btnComplete.disabled = false;
      btnStop.disabled = false;
    }

    // Only show auto tick toggle during ACTIVE execution
    if (status === 'ACTIVE') {
      tickWrapper.classList.add('visible');
    } else {
      tickWrapper.classList.remove('visible');
      const toggleTick = document.getElementById('toggle-auto-tick');
      if (toggleTick && toggleTick.checked) {
        toggleTick.checked = false;
        this.handleToggleAutoTick(false);
      }
    }
  }

  // --- Form Handlers ---
  async handleCreateMission(e) {
    e.preventDefault();

    const name = document.getElementById('mission-name-input').value.trim();
    const sopProfileId = document.getElementById('mission-sop-profile').value;
    const priority = document.getElementById('mission-priority-select').value;

    if (!name) {
      this.showToast('미션 이름을 입력해 주세요.', 'warning');
      return;
    }

    // Generate random polygon coordinates near center map
    const coords = [
      { x: -5.0 + Math.random() * 2, y: -5.0 + Math.random() * 2, z: 0.0 },
      { x: 12.0 + Math.random() * 2, y: -3.0 + Math.random() * 2, z: 0.0 },
      { x: 5.0 + Math.random() * 2, y: 15.0 + Math.random() * 2, z: 0.0 },
    ];

    const randomId = 'REQ-' + Math.floor(1000 + Math.random() * 9000);

    const payload = {
      request_id: randomId,
      operator_id: 'OP-DASHBOARD',
      mission_name: name,
      search_area: {
        area_type: 'POLYGON',
        coordinates: coords,
        frame_id: 'map',
      },
      search_method: 'PARALLEL_SWEEP',
      sop_profile_id: sopProfileId,
      priority: priority,
      created_at_ms: Date.now(),
    };

    try {
      const res = await window.apiClient.createMission(payload);
      this.showToast(`미션 ${res.mission_id} 드래프트가 성공적으로 생성되었습니다.`, 'success');
      document.getElementById('mission-name-input').value = '';
      
      // Auto refresh lists
      await this.refreshMissionsList();
      this.selectActiveMission(res.mission_id);
    } catch (err) {
      this.showToast(`임무 생성 실패: ${err.message}`, 'error');
    }
  }

  // --- Control Button Handlers ---
  async handleApprove() {
    if (!this.activeMissionId) return;
    try {
      const plan = await window.apiClient.approveMission(this.activeMissionId, 'FIELD_CDR_DASHBOARD');
      this.showToast(`미션 계획 승인 완료. (Snapshot: ${plan.plan_snapshot_id})`, 'success');
      this.selectActiveMission(this.activeMissionId);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  async handleStart() {
    if (!this.activeMissionId) return;
    try {
      const res = await window.apiClient.startMission(this.activeMissionId);
      this.showToast(`로봇 실시간 SAR 탐색 임무를 개시합니다.`, 'success');
      this.selectActiveMission(this.activeMissionId);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  async handleComplete() {
    if (!this.activeMissionId) return;
    try {
      await window.apiClient.completeMission(this.activeMissionId);
      this.showToast(`임무 완료 처리되었습니다. 로봇 복귀 지령을 송신합니다.`, 'success');
      this.selectActiveMission(this.activeMissionId);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  async handleEmergencyStop() {
    if (!this.activeMissionId) return;
    try {
      await window.apiClient.emergencyStop(this.activeMissionId);
      this.showToast(`🔴 로봇 물리 비상 정지(EMERGENCY STOP) 명령이 하달되었습니다.`, 'error');
      this.selectActiveMission(this.activeMissionId);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }

  // --- Auto-Tick Telemetry Simulator ---
  handleToggleAutoTick(checked) {
    if (checked) {
      console.log('Auto-Tick Telemetry Simulator Active.');
      this.autoTickInterval = setInterval(async () => {
        if (!this.activeMissionId) return;
        try {
          const details = await window.apiClient.tickMission(this.activeMissionId);
          
          // Render changes instantly
          Components.renderMissionDetails(details, document.getElementById('active-mission-details'));
          Components.renderDetectionFeed(details.detections, document.getElementById('detection-alerts-container'));
          
          const canvas = document.getElementById('terrain-canvas');
          Components.renderTerrainMapCanvas(canvas, details);

          this.updateControlPanelButtons(details.status);

          if (details.status === 'COMPLETED') {
            this.showToast('미션 커버리지 100% 도달하여 임무가 안전하게 마무리되었습니다.', 'success');
            document.getElementById('toggle-auto-tick').checked = false;
            this.handleToggleAutoTick(false);
          }
        } catch (err) {
          console.error('Tick failed:', err);
        }
      }, 1500);
    } else {
      console.log('Auto-Tick Telemetry Simulator Paused.');
      if (this.autoTickInterval) {
        clearInterval(this.autoTickInterval);
        this.autoTickInterval = null;
      }
    }
  }

  // --- Dynamic Toast Alert Helper ---
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'alert-octagon' : 'info'}"></i> <span>${message}</span>`;
    
    document.getElementById('toast-container').appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  }
}

// Start app
window.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
  window.app.init();
});
