import { NavLink, Route, Routes } from "react-router-dom";
import ExecutivePage from "./pages/ExecutivePage";
import RegulatoryPage from "./pages/RegulatoryPage";
import MapPage from "./pages/MapPage";

function NavTabs() {
  return (
    <nav className="nav-tabs">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Executive
      </NavLink>
      <NavLink
        to="/regulatory"
        className={({ isActive }) => (isActive ? "tab active" : "tab")}
      >
        Regulatory
      </NavLink>
      <NavLink to="/map" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        City Map
      </NavLink>
    </nav>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="dot" />
          <div>
            <div className="title">Dr. Ian Helfrich Strategy Lab</div>
            <div className="subtitle">Costco Germany 2026 | Real-Options Command Center</div>
          </div>
        </div>
        <a
          className="external-link"
          href="https://github.com/ihelfrich/GermanCostCo"
          target="_blank"
          rel="noreferrer"
        >
          Project Repository
        </a>
      </header>

      <NavTabs />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<ExecutivePage />} />
          <Route path="/regulatory" element={<RegulatoryPage />} />
          <Route path="/map" element={<MapPage />} />
        </Routes>
      </main>
    </div>
  );
}
