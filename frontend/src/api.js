import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// ── Dashboard ─────────────────────────────────────────
export const fetchDashboard = () => api.get("/api/dashboard/");

// ── Sensor Data ───────────────────────────────────────
export const fetchSensorData = (params) =>
  api.get("/api/sensor-data/", { params });

export const fetchLatestReadings = (limit = 10) =>
  api.get("/api/sensor-data/latest", { params: { limit } });

export const fetchTopics = () => api.get("/api/sensor-data/topics");

// ── Alerts ────────────────────────────────────────────
export const fetchAlerts = (params) =>
  api.get("/api/alerts/", { params });

export const fetchActiveAlerts = (limit = 20) =>
  api.get("/api/alerts/active", { params: { limit } });

export const resolveAlert = (alertId) =>
  api.patch(`/api/alerts/${alertId}/resolve`);

export default api;
