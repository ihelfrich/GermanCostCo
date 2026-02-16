import { useMemo, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import { usePresentationData } from "../utils/usePresentationData";
import { formatEur, formatPct } from "../utils/format";
import type { CityRow } from "../types";

const WAVE_COLORS: Record<string, string> = {
  "Wave 1 Pilot": "#b71c1c",
  "Wave 2 Scale": "#ef6c00",
  "Wave 3 Option": "#546e7a",
  Hold: "#8e8e8e",
};

function unique<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}

export default function MapPage() {
  const { data, loading, error } = usePresentationData();
  const rows = useMemo(() => {
    const values = (data?.city_portfolio_plan || data?.city_recommendations || []) as CityRow[];
    return [...values].sort((a, b) => Number(a.city_rank) - Number(b.city_rank));
  }, [data]);

  const [wave, setWave] = useState<string>("ALL");
  const [signal, setSignal] = useState<string>("ALL");

  const waves = useMemo(() => unique(rows.map((r) => r.launch_wave)).sort(), [rows]);
  const signals = useMemo(() => unique(rows.map((r) => r.board_signal)).sort(), [rows]);

  const filteredRows = useMemo(
    () =>
      rows.filter((r) => {
        if (wave !== "ALL" && r.launch_wave !== wave) return false;
        if (signal !== "ALL" && r.board_signal !== signal) return false;
        return true;
      }),
    [rows, wave, signal]
  );

  const portfolioSummary = useMemo(() => {
    const selected = rows.filter((row) => Number(row.rollout_year || -1) > 0);
    const contribution = selected.reduce((acc, row) => acc + Number(row.expected_contribution_eur || 0), 0);
    const capex = selected.reduce((acc, row) => acc + Number(row.capex_estimate_eur || 0), 0);
    return {
      selectedCount: selected.length,
      totalContribution: contribution,
      totalCapex: capex,
      avgLoss: selected.length
        ? selected.reduce((acc, row) => acc + Number(row.city_prob_loss || 0), 0) / selected.length
        : 0,
    };
  }, [rows]);

  if (loading) return <div className="state-box">Loading city portfolio...</div>;
  if (error) return <div className="state-box error">{error}</div>;

  return (
    <section className="page-block">
      <div className="hero-card map-hero">
        <p className="eyebrow">Rollout Optimizer</p>
        <h1>City Portfolio Map</h1>
        <p>Filter launch waves and board signals for location-level rollout sequencing.</p>
      </div>

      <article className="panel">
        <h2>Portfolio Doctrine</h2>
        <p className="panel-subtext">
          Sequence for option value, not for map coverage. Expansion rights are earned by contribution quality and
          governance reliability.
        </p>
        <div className="kpi-grid">
          <article className="kpi-card">
            <div className="kpi-label">Selected Cities</div>
            <div className="kpi-value">{portfolioSummary.selectedCount}</div>
          </article>
          <article className="kpi-card">
            <div className="kpi-label">Total Expected Contribution</div>
            <div className="kpi-value">{formatEur(portfolioSummary.totalContribution, 0)}</div>
          </article>
          <article className="kpi-card">
            <div className="kpi-label">Total Capex</div>
            <div className="kpi-value">{formatEur(portfolioSummary.totalCapex, 0)}</div>
          </article>
          <article className="kpi-card">
            <div className="kpi-label">Average Loss Risk</div>
            <div className="kpi-value">{formatPct(portfolioSummary.avgLoss, 1)}</div>
          </article>
        </div>
      </article>

      <article className="panel">
        <div className="filter-row">
          <label>
            Launch Wave
            <select value={wave} onChange={(e) => setWave(e.target.value)}>
              <option value="ALL">All</option>
              {waves.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
          </label>
          <label>
            Board Signal
            <select value={signal} onChange={(e) => setSignal(e.target.value)}>
              <option value="ALL">All</option>
              {signals.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="map-wrap">
          <MapContainer
            center={[51.1657, 10.4515]}
            zoom={6}
            style={{ width: "100%", height: "520px", borderRadius: "12px" }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {filteredRows.map((row) => {
              const color = WAVE_COLORS[row.launch_wave] || "#8e8e8e";
              return (
                <CircleMarker
                  key={`${row.city}-${row.strategy}`}
                  center={[Number(row.lat), Number(row.lon)]}
                  pathOptions={{ color, fillColor: color, fillOpacity: 0.6 }}
                  radius={7 + Math.max(0, Number(row.city_rank ? 14 - row.city_rank / 2 : 4))}
                >
                  <Popup>
                    <div className="popup">
                      <strong>
                        {row.city}, {row.state}
                      </strong>
                      <div>Wave: {row.launch_wave}</div>
                      <div>Signal: {row.board_signal}</div>
                      <div>Strategy: {row.strategy}</div>
                      <div>Contribution: {formatEur(Number(row.expected_contribution_eur || 0), 0)}</div>
                      <div>Loss Risk: {formatPct(Number(row.city_prob_loss || 0), 1)}</div>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>
      </article>

      <article className="panel">
        <h2>Filtered City Ranking</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>City</th>
                <th>Wave</th>
                <th>Signal</th>
                <th>Strategy</th>
                <th>Contribution</th>
                <th>Loss</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row) => (
                <tr key={`${row.city}-${row.strategy}-table`}>
                  <td>{row.city_rank}</td>
                  <td>
                    <strong>{row.city}</strong>
                    <div className="small-text">{row.state}</div>
                  </td>
                  <td>{row.launch_wave}</td>
                  <td>{row.board_signal}</td>
                  <td>{row.strategy}</td>
                  <td>{formatEur(Number(row.expected_contribution_eur || 0), 0)}</td>
                  <td>{formatPct(Number(row.city_prob_loss || 0), 1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
