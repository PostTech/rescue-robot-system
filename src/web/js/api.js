/**
 * API Client for the Rescue Robot System.
 * Handles standard fetch requests to the FastAPI backend.
 */
class ApiClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async _request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errMsg = `HTTP Error ${response.status}`;
        try {
          const errData = await response.json();
          errMsg = errData.detail || errMsg;
        } catch (_) {}
        throw new Error(errMsg);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Request to ${path} failed:`, error);
      throw error;
    }
  }

  // --- Missions API ---
  getMissions() {
    return this._request('/api/missions');
  }

  getMissionDetails(missionId) {
    return this._request(`/api/missions/${missionId}`);
  }

  createMission(payload) {
    return this._request('/api/missions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  approveMission(missionId, approver) {
    return this._request(`/api/missions/${missionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approver }),
    });
  }

  startMission(missionId) {
    return this._request(`/api/missions/${missionId}/start`, {
      method: 'POST',
    });
  }

  completeMission(missionId) {
    return this._request(`/api/missions/${missionId}/complete`, {
      method: 'POST',
    });
  }

  emergencyStop(missionId) {
    return this._request(`/api/missions/${missionId}/emergency-stop`, {
      method: 'POST',
    });
  }

  tickMission(missionId) {
    return this._request(`/api/missions/${missionId}/tick`, {
      method: 'POST',
    });
  }

  // --- SOP API ---
  getSopProfiles() {
    return this._request('/api/sop/profiles');
  }

  // --- Terrain API ---
  analyzeTerrain(missionId, payload) {
    return this._request(`/api/terrain/${missionId}/analyze`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  getTerrainHistory(missionId) {
    return this._request(`/api/terrain/${missionId}/history`);
  }

  // --- Detection API ---
  analyzeDetection(missionId, payload) {
    return this._request(`/api/detection/${missionId}/analyze`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Safety & Events API ---
  getSafetyStatus() {
    return this._request('/api/safety/status');
  }

  getEvents() {
    return this._request('/api/events');
  }
}

// Export for browser usage
window.apiClient = new ApiClient();
