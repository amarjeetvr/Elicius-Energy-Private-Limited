import React, { useEffect, useState, useCallback } from "react";
import { fetchAlerts, resolveAlert, fetchTopics } from "../api";

function AlertsPage() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [topic, setTopic] = useState("");
  const [severity, setSeverity] = useState("");
  const [resolved, setResolved] = useState("");
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 20 };
      if (topic) params.topic = topic;
      if (severity) params.severity = severity;
      if (resolved !== "") params.resolved = parseInt(resolved, 10);

      const [alertsRes, topicsRes] = await Promise.all([
        fetchAlerts(params),
        topics.length ? Promise.resolve({ data: topics }) : fetchTopics(),
      ]);
      setData(alertsRes.data);
      if (!topics.length) setTopics(topicsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, topic, severity, resolved, topics.length]);

  useEffect(() => { load(); }, [load]);

  const handleResolve = async (id) => {
    try {
      await resolveAlert(id);
      load();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Alerts</h1>
        <p>All threshold-breach alerts with metadata and status</p>
      </div>

      {/* Filters */}
      <div className="filters">
        <select value={topic} onChange={(e) => { setTopic(e.target.value); setPage(1); }}>
          <option value="">All Topics</option>
          {topics.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <select value={severity} onChange={(e) => { setSeverity(e.target.value); setPage(1); }}>
          <option value="">All Severities</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
        </select>

        <select value={resolved} onChange={(e) => { setResolved(e.target.value); setPage(1); }}>
          <option value="">All Status</option>
          <option value="0">Active</option>
          <option value="1">Resolved</option>
        </select>
      </div>

      {loading && <div className="loading">Loading…</div>}

      {!loading && data && (
        <div className="card">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Timestamp</th>
                  <th>Topic</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Violated Params</th>
                  <th>Actual Values</th>
                  <th>Threshold Limits</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="empty">No alerts found.</td>
                  </tr>
                ) : (
                  data.items.map((a) => (
                    <tr key={a.id}>
                      <td>{a.id}</td>
                      <td style={{ whiteSpace: "nowrap" }}>
                        {new Date(a.created_at).toLocaleString()}
                      </td>
                      <td>{a.topic}</td>
                      <td>
                        <span className={`badge ${a.severity}`}>{a.severity}</span>
                      </td>
                      <td>
                        <span className={`badge ${a.resolved ? "resolved" : "critical"}`}>
                          {a.resolved ? "Resolved" : "Active"}
                        </span>
                      </td>
                      <td>
                        {a.violated_keys.map((k) => (
                          <span className="badge param" key={k}>{k}</span>
                        ))}
                      </td>
                      <td style={{ fontSize: "0.8rem" }}>
                        {Object.entries(a.actual_values).map(([k, v]) => (
                          <div key={k}>
                            <strong>{k}:</strong> {typeof v === "number" ? v.toFixed(2) : v}
                          </div>
                        ))}
                      </td>
                      <td style={{ fontSize: "0.8rem" }}>
                        {Object.entries(a.threshold_limits).map(([k, lim]) => (
                          <div key={k}>
                            <strong>{k}:</strong> {lim.min}–{lim.max}
                          </div>
                        ))}
                      </td>
                      <td>
                        {!a.resolved && (
                          <button
                            onClick={() => handleResolve(a.id)}
                            style={{
                              background: "var(--success)",
                              color: "#fff",
                              border: "none",
                              padding: "6px 12px",
                              borderRadius: 6,
                              cursor: "pointer",
                              fontSize: "0.8rem",
                              fontWeight: 600,
                            }}
                          >
                            Resolve
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
              ← Prev
            </button>
            <span className="page-info">
              Page {data.page} of {data.total_pages} ({data.total} total)
            </span>
            <button disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AlertsPage;
