/**
 * Demo Scenario UI Controller.
 * Binds demo triggers to API endpoints and renders real-time stage explanation cards.
 */
class DemoController {
  constructor() {
    this.overlayEl = null;
  }

  init() {
    console.log('[DemoController] Initializing...');
    this.createOverlayElement();
    this.bindDemoButtons();
  }

  createOverlayElement() {
    // Append a floating explanation overlay panel dynamically to the center column
    const centerPanel = document.querySelector('.panel-center');
    if (!centerPanel) return;

    const overlay = document.createElement('div');
    overlay.id = 'demo-walkthrough-overlay';
    overlay.className = 'demo-walkthrough-overlay';
    overlay.innerHTML = `
      <div class="demo-overlay-header">
        <span class="demo-badge"><i data-lucide="info"></i> 시연 가이드</span>
        <button class="btn-close-overlay" onclick="window.demoController.hideOverlay()">&times;</button>
      </div>
      <div class="demo-overlay-content">
        <h4 id="demo-stage-title">시나리오 시연을 시작해 주세요.</h4>
        <p id="demo-stage-text">하단 제어 보드의 데모 버튼 중 하나를 클릭하면 100% 자동 모의 시연이 시작됩니다.</p>
      </div>
    `;

    centerPanel.insertBefore(overlay, centerPanel.querySelector('.active-mission-details'));
    this.overlayEl = overlay;
    lucide.createIcons();
  }

  bindDemoButtons() {
    // Bind click events on the bottom controls
    const btnGroup = document.querySelector('.btn-group');
    if (!btnGroup) return;

    // Create a sleek new sub-panel for demo controls at the top of Sidebar Panel Left
    const leftPanel = document.querySelector('.panel-left');
    if (!leftPanel) return;

    const demoWidget = document.createElement('div');
    demoWidget.className = 'demo-widget-card';
    demoWidget.innerHTML = `
      <div class="widget-header">
        <i data-lucide="play"></i>
        <span>자동 모의 시연 (SAR Scenarios)</span>
      </div>
      <div class="demo-btn-grid">
        <button class="btn btn-demo btn-mnt" onclick="window.demoController.triggerDemo('mountain')">
          <i data-lucide="mountain"></i> 산악 실종
        </button>
        <button class="btn btn-demo btn-col" onclick="window.demoController.triggerDemo('collapsed')">
          <i data-lucide="home"></i> 건물 붕괴
        </button>
        <button class="btn btn-demo btn-tnl" onclick="window.demoController.triggerDemo('tunnel')">
          <i data-lucide="train"></i> 터널 침수
        </button>
      </div>
    `;

    // Insert as the first child of panel-left
    leftPanel.insertBefore(demoWidget, leftPanel.firstChild);
    lucide.createIcons();
  }

  async triggerDemo(scenario) {
    if (window.app) {
      window.app.showToast(`[시연 시작] '${scenario === 'mountain' ? '산악 수색' : scenario === 'collapsed' ? '붕괴 구조' : '터널 가스'}' 시나리오를 개시합니다.`, 'info');
    }

    try {
      const response = await fetch(`http://localhost:8000/api/demo/start/${scenario}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('시나리오 구동 실패');
      
      const res = await response.json();
      console.log('Demo started:', res);
      this.showOverlay(1, "시나리오 준비 중... 서버 푸시 대기 중.");
    } catch (err) {
      if (window.app) {
        window.app.showToast(`데모 트리거 에러: ${err.message}`, 'error');
      }
    }
  }

  showOverlay(stage, text) {
    if (!this.overlayEl) return;

    const titleEl = document.getElementById('demo-stage-title');
    const textEl = document.getElementById('demo-stage-text');

    if (titleEl && textEl) {
      titleEl.innerHTML = `<i data-lucide="cpu" class="blink-icon"></i> 시나리오 진행 단계 #${stage}`;
      textEl.textContent = text;
      this.overlayEl.classList.add('active');
      lucide.createIcons();
    }
  }

  hideOverlay() {
    if (this.overlayEl) {
      this.overlayEl.classList.remove('active');
    }
  }
}

// Start demo controller
window.addEventListener('DOMContentLoaded', () => {
  window.demoController = new DemoController();
  window.demoController.init();
});
