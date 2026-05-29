/**
 * WebSocket client for Rescue Robot System.
 * Establishes real-time connection to server, listens for EventBus push streams,
 * and triggers reactive UI updates with automatic self-healing reconnects.
 */
class WebSocketClient {
  constructor(wsUrl = 'ws://localhost:8000/ws') {
    this.wsUrl = wsUrl;
    this.socket = null;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 16000;
    this.isConnecting = false;
  }

  connect() {
    if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    console.log(`[WebSocket] Connecting to ${this.wsUrl}...`);
    this.isConnecting = true;
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onopen = () => {
      console.log('[WebSocket] Connection established successfully.');
      this.isConnecting = false;
      this.reconnectDelay = 1000; // Reset delay on success
      
      // Update UI Header indicator or show safe connection toast
      if (window.app) {
        window.app.showToast('실시간 소켓 서버와 연결되었습니다.', 'success');
      }
    };

    this.socket.onmessage = async (event) => {
      try {
        const payload = JSON.parse(event.data);
        console.log('[WebSocket] Message received:', payload);
        
        await this.handleServerEvent(payload);
      } catch (err) {
        console.error('[WebSocket] Failed to parse socket message:', err);
      }
    };

    this.socket.onclose = (event) => {
      this.isConnecting = false;
      this.socket = null;
      console.warn(`[WebSocket] Closed (Code: ${event.code}). Attempting reconnect...`);
      
      // Handle reconnect with exponential backoff
      setTimeout(() => {
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
        this.connect();
      }, this.reconnectDelay);
    };

    this.socket.onerror = (error) => {
      console.error('[WebSocket] Error occurred:', error);
      // Let onclose handle the reconnection flow
    };
  }

  /**
   * Processes domain EventBus events sent via websocket
   */
  async handleServerEvent(payload) {
    // Handle demo walkthrough annotations pushed from backend simulation track
    if (payload.event_type === 'demo.stage') {
      if (window.demoController) {
        window.demoController.showOverlay(payload.data.stage, payload.data.description);
      }
      return;
    }

    // Handle live camera frames pushed from video publisher
    if (payload.event_type === 'video.frame') {
      const imgEl = document.getElementById('live-camera-feed');
      const placeholder = document.getElementById('camera-placeholder');
      if (imgEl && placeholder) {
        imgEl.src = `data:image/jpeg;base64,${payload.data.frame_data}`;
        placeholder.style.display = 'none';
        imgEl.style.display = 'block';
      }
      return;
    }

    if (payload.event_type !== 'event.published') return;

    const data = payload.data;
    if (!data) return;

    // 1. Reactive Update: Update active mission details instantly on relevant changes
    if (window.app && window.app.activeMissionId === data.mission_id) {
      console.log(`[WebSocket] Reactive update triggered for mission: ${data.mission_id}`);
      
      // Instantly refresh active mission context details, alerts list, and canvas map
      await window.app.selectActiveMission(data.mission_id);

      // Play alert sound mock or show popup for specific critical events
      if (data.event_type === 'EMERGENCY_STOP') {
        window.app.showToast('🔴 로봇 비상 정지(EMERGENCY STOP) 경보가 수신되었습니다!', 'error');
      }
    }

    // 2. Refresh lists and summaries automatically
    if (window.app) {
      await window.app.refreshMissionsList();
      await window.app.updateSafetyStatus();
      await window.app.updateEventTimeline();
      
      // Auto scroll event logs container down to show the latest activity
      const logContainer = document.getElementById('event-timeline-container');
      if (logContainer) {
        logContainer.scrollTop = 0; // Highlight latest chronologically (sorted latest first)
      }
    }
  }
}

// Start WebSocket connection automatically on load
window.addEventListener('DOMContentLoaded', () => {
  window.wsClient = new WebSocketClient();
  window.wsClient.connect();
});
