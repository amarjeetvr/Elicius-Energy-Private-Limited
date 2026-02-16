import React, { useEffect, useState, useCallback } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from "recharts";
import { fetchDashboard, fetchActiveAlerts } from "../api";

const PARAM_COLORS = {
  temperature: "#ef4444",
  humidity: "#3b82f6",
  voltage: "#f59e0b",
  current: "#22c55e",
  pressure: "#a855f7",
};

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [dashRes, alertRes] = await Promise.all([
        fetchDashboard(),
        fetchActiveAlerts(10),
      ]);
      setStats(dashRes.data);
      setActiveAlerts(alertRes.data);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000); // Auto-refresh every 5 s
    return () => clearInterval(interval);
  }, [load]);

  if (loading) return <div className="loading">Loading dashboard…</div>;
  if (!stats) return <div className="empty">Unable to load dashboard data.</div>;

  // Build chart data from latest_readings
  const chartData = Object.entries(stats.latest_readings).map(([topic, vals]) => ({
    topic: topic.replace("sensor/", ""),
    ...vals,
  }));

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of sensor data and system health</p>
      </div>

      {/* Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Total Messages</span>
          <span className="stat-value blue">{stats.total_messages.toLocaleString()}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Alerts</span>
          <span className="stat-value yellow">{stats.total_alerts.toLocaleString()}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Active Alerts</span>
          <span className="stat-value red">{stats.active_alerts.toLocaleString()}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Topics</span>
          <span className="stat-value green">{stats.topics.length}</span>
        </div>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ marginBottom: 16, fontSize: "1.1rem" }}>Latest Readings by Topic</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="topic" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                labelStyle={{ color: "#f1f5f9" }}
              />
              <Legend />
              {Object.keys(PARAM_COLORS).map((param) => (
                <Bar
                  key={param}
                  dataKey={param}
                  fill={PARAM_COLORS[param]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Latest Readings Cards */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 8, fontSize: "1.1rem" }}>Latest Sensor Readings</h2>
        <div className="readings-grid">
          {Object.entries(stats.latest_readings).map(([topic, vals]) => (
            <div className="reading-card" key={topic}>
              <h3>{topic}</h3>
              <div className="reading-params">
                {Object.entries(vals).map(([k, v]) =>
                  k !== "received_at" && v !== null ? (
                    <div className="param-item" key={k}>
                      <span className="param-name">{k}</span>
                      <span className="param-value">{typeof v === "number" ? v.toFixed(2) : v}</span>
                    </div>
                  ) : null
                )}
              </div>
              {vals.received_at && (
                <p style={{ color: "var(--text-secondary)", fontSize: "0.75rem", marginTop: 8 }}>
                  {new Date(vals.received_at).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Active Alerts */}
      <div className="card">
        <h2 style={{ marginBottom: 16, fontSize: "1.1rem" }}>
          Recent Active Alerts ({activeAlerts.length})
        </h2>
        {activeAlerts.length === 0 ? (
          <p className="empty">No active alerts — all systems normal.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Topic</th>
                  <th>Severity</th>
                  <th>Violated Params</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {activeAlerts.map((a) => (
                  <tr key={a.id}>
                    <td>{new Date(a.created_at).toLocaleString()}</td>
                    <td>{a.topic}</td>
                    <td>
                      <span className={`badge ${a.severity}`}>{a.severity}</span>
                    </td>
                    <td>
                      {a.violated_keys.map((k) => (
                        <span className="badge param" key={k}>{k}</span>
                      ))}
                    </td>
                    <td style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      {a.message}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
