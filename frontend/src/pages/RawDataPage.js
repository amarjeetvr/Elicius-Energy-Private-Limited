import React, { useEffect, useState, useCallback } from "react";
import { fetchSensorData, fetchTopics } from "../api";

function RawDataPage() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [topic, setTopic] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 25 };
      if (topic) params.topic = topic;
      if (startTime) params.start_time = startTime;
      if (endTime) params.end_time = endTime;

      const [sensorRes, topicsRes] = await Promise.all([
        fetchSensorData(params),
        topics.length ? Promise.resolve({ data: topics }) : fetchTopics(),
      ]);
      setData(sensorRes.data);
      if (!topics.length) setTopics(topicsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, topic, startTime, endTime, topics.length]);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <div className="page-header">
        <h1>Raw Sensor Data</h1>
        <p>Full tabular view of all incoming MQTT messages</p>
      </div>

      {/* Filters */}
      <div className="filters">
        <select value={topic} onChange={(e) => { setTopic(e.target.value); setPage(1); }}>
          <option value="">All Topics</option>
          {topics.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <label style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          From:
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => { setStartTime(e.target.value); setPage(1); }}
            style={{ marginLeft: 4 }}
          />
        </label>

        <label style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          To:
          <input
            type="datetime-local"
            value={endTime}
            onChange={(e) => { setEndTime(e.target.value); setPage(1); }}
            style={{ marginLeft: 4 }}
          />
        </label>
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
                  <th>Temperature</th>
                  <th>Humidity</th>
                  <th>Voltage</th>
                  <th>Current</th>
                  <th>Pressure</th>
                </tr>
              </thead>
              <tbody>
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty">No data found.</td>
                  </tr>
                ) : (
                  data.items.map((row) => (
                    <tr key={row.id}>
                      <td>{row.id}</td>
                      <td style={{ whiteSpace: "nowrap" }}>
                        {new Date(row.received_at).toLocaleString()}
                      </td>
                      <td>{row.topic}</td>
                      <td>{row.temperature !== null ? row.temperature.toFixed(2) : "—"}</td>
                      <td>{row.humidity !== null ? row.humidity.toFixed(2) : "—"}</td>
                      <td>{row.voltage !== null ? row.voltage.toFixed(2) : "—"}</td>
                      <td>{row.current !== null ? row.current.toFixed(2) : "—"}</td>
                      <td>{row.pressure !== null ? row.pressure.toFixed(2) : "—"}</td>
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

export default RawDataPage;
