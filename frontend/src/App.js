import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import { LayoutDashboard, AlertTriangle, Database, Zap } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import AlertsPage from "./pages/AlertsPage";
import RawDataPage from "./pages/RawDataPage";

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="logo">
            <Zap size={24} />
            <span className="logo-text">Energy Monitor</span>
          </div>

          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            <LayoutDashboard size={20} />
            <span className="nav-text">Dashboard</span>
          </NavLink>

          <NavLink
            to="/alerts"
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            <AlertTriangle size={20} />
            <span className="nav-text">Alerts</span>
          </NavLink>

          <NavLink
            to="/raw-data"
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            <Database size={20} />
            <span className="nav-text">Raw Data</span>
          </NavLink>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/raw-data" element={<RawDataPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
