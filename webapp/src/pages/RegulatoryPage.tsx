import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatEur, formatNumber } from "../utils/format";
import { usePresentationData } from "../utils/usePresentationData";
import type { RegulatoryRow } from "../types";

export default function RegulatoryPage() {
  const { data, loading, error } = usePresentationData();
  const rows = useMemo(() => (data?.regulatory_environment || []) as RegulatoryRow[], [data]);
  const summary = data?.regulatory_summary;

  if (loading) return <div className="state-box">Loading regulatory intelligence...</div>;
  if (error) return <div className="state-box error">{error}</div>;
  if (!rows.length) return <div className="state-box error">No regulatory data found in payload.</div>;

  const timelineRows = [...rows]
    .filter((r) => !!r.effective_date)
    .sort((a, b) => new Date(a.effective_date).getTime() - new Date(b.effective_date).getTime())
    .map((r) => ({
      ...r,
      year: new Date(r.effective_date).getFullYear(),
      x: new Date(r.effective_date).getTime(),
      y: r.severity_score_1_to_5,
      z: r.likelihood_score_1_to_5,
    }));

  const ownerRows = Object.entries(
    rows.reduce<Record<string, number>>((acc, row) => {
      const key = row.operational_owner || "Unknown";
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {})
  ).map(([owner, count]) => ({ owner, count }));

  const sortedBySeverity = [...rows].sort((a, b) => {
    if (b.severity_score_1_to_5 !== a.severity_score_1_to_5) {
      return b.severity_score_1_to_5 - a.severity_score_1_to_5;
    }
    return new Date(a.effective_date).getTime() - new Date(b.effective_date).getTime();
  });

  return (
    <section className="page-block">
      <div className="hero-card regulatory">
        <p className="eyebrow">Dedicated Legal View</p>
        <h1>Regulatory Environment and Concerns</h1>
        <p>
          Statute-level register with deadlines, sanctions, and control ownership for launch governance.
        </p>
      </div>

      <div className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">Total Obligations</div>
          <div className="kpi-value">{formatNumber(Number(summary?.count_total || rows.length), 0)}</div>
        </article>
        <article className="kpi-card">
          <div className="kpi-label">High Severity (5/5)</div>
          <div className="kpi-value">{formatNumber(Number(summary?.count_high_severity || 0), 0)}</div>
        </article>
        <article className="kpi-card">
          <div className="kpi-label">Near-Term 2026-2027</div>
          <div className="kpi-value">{formatNumber(Number(summary?.near_term_2026_2027 || 0), 0)}</div>
        </article>
        <article className="kpi-card">
          <div className="kpi-label">Largest Explicit Fine</div>
          <div className="kpi-value">{formatEur(Number(summary?.max_explicit_fine_eur || 0), 0)}</div>
        </article>
      </div>

      <div className="panel-grid">
        <article className="panel">
          <h2>Regulatory Timeline</h2>
          <div style={{ width: "100%", height: 350 }}>
            <ResponsiveContainer>
              <ScatterChart margin={{ top: 10, right: 18, left: 8, bottom: 10 }}>
                <CartesianGrid />
                <XAxis
                  dataKey="x"
                  type="number"
                  domain={["dataMin", "dataMax"]}
                  tickFormatter={(value) => new Date(Number(value)).getFullYear().toString()}
                  name="Date"
                />
                <YAxis dataKey="y" type="number" domain={[1, 5]} name="Severity" />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  formatter={(value: number, key: string) => {
                    if (key === "x") return new Date(Number(value)).toISOString().slice(0, 10);
                    return Number(value).toFixed(0);
                  }}
                  labelFormatter={(_, payload) =>
                    payload && payload[0]?.payload ? payload[0].payload.regulation : ""
                  }
                />
                <Scatter data={timelineRows} fill="#b71c1c" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel">
          <h2>Severity vs Likelihood</h2>
          <div style={{ width: "100%", height: 350 }}>
            <ResponsiveContainer>
              <ScatterChart margin={{ top: 10, right: 18, left: 8, bottom: 10 }}>
                <CartesianGrid />
                <XAxis dataKey="likelihood_score_1_to_5" type="number" domain={[1, 5]} name="Likelihood" />
                <YAxis dataKey="severity_score_1_to_5" type="number" domain={[1, 5]} name="Severity" />
                <Tooltip
                  labelFormatter={(_, payload) =>
                    payload && payload[0]?.payload
                      ? `${payload[0].payload.category}: ${payload[0].payload.regulation}`
                      : ""
                  }
                />
                <Scatter data={rows} fill="#6e6e6e" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </article>
      </div>

      <article className="panel">
        <h2>Control Ownership</h2>
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <BarChart data={ownerRows} margin={{ top: 10, right: 20, left: 10, bottom: 45 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="owner" angle={-15} textAnchor="end" interval={0} height={70} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#6e6e6e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="panel">
        <h2>Full Regulatory Register</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Regulation</th>
                <th>Requirement</th>
                <th>Sanction</th>
                <th>Sev</th>
                <th>Lik</th>
                <th>Owner</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {sortedBySeverity.map((row) => (
                <tr key={row.id}>
                  <td>{row.effective_date}</td>
                  <td>{row.category}</td>
                  <td>
                    <strong>{row.regulation}</strong>
                    <div className="small-text">{row.deadline_or_trigger}</div>
                  </td>
                  <td>{row.requirement}</td>
                  <td>{row.maximum_sanction}</td>
                  <td>{row.severity_score_1_to_5}</td>
                  <td>{row.likelihood_score_1_to_5}</td>
                  <td>{row.operational_owner}</td>
                  <td>
                    <a href={row.source_url} target="_blank" rel="noreferrer">
                      Source
                    </a>
                    <div className="small-text">{row.source_note}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
