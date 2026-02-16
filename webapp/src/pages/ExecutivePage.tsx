import { useMemo } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatEur, formatNumber, formatPct } from "../utils/format";
import { usePresentationData } from "../utils/usePresentationData";
import type { DecisionRow, ScenarioRow } from "../types";

function unique<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}

export default function ExecutivePage() {
  const { data, loading, error } = usePresentationData();

  const decisionRows = useMemo(
    () => [...(data?.decision_matrix || [])].sort((a, b) => Number(a.rank) - Number(b.rank)),
    [data]
  );
  const scenarioRows = useMemo(() => (data?.scenario_summary || []) as ScenarioRow[], [data]);
  const topStrategy = data?.key_decision?.top_strategy || "subsidized_65_to_20";

  const topBaseRow = useMemo(
    () => scenarioRows.find((row) => row.scenario === "base_case" && row.strategy === topStrategy),
    [scenarioRows, topStrategy]
  );

  const kpis = useMemo(() => {
    const exec = data?.executive_summary || {};
    const decision = data?.key_decision || {};
    return [
      { label: "Recommended Strategy", value: decision.top_strategy || "-" },
      {
        label: "5Y NPV",
        value: formatEur(Number(exec.recommended_strategy_npv_5y_eur || 0), 0),
      },
      {
        label: "Base Loss Probability",
        value: formatPct(Number(exec.base_standard_prob_loss || 0), 1),
      },
      {
        label: "Marketing Reject Count",
        value: formatNumber(Number(exec.marketing_reject_count || 0), 0),
      },
      {
        label: "Data Refresh Health",
        value: `${formatNumber(Number(exec.refresh_ok_sources || 0), 0)}/${formatNumber(
          Number(exec.refresh_total_sources || 0),
          0
        )}`,
      },
    ];
  }, [data]);

  const partnerInsights = useMemo(() => {
    const macro = data?.macro || {};
    const cultural = data?.cultural || {};
    const compliance = data?.executive_summary?.compliance_summary || {};
    return [
      `Germany is a proof market, not a persuasion market: climate ${formatNumber(Number(macro.consumer_climate_index || 0), 1)} with savings pressure ${formatNumber(Number(macro.savings_rate_percent || 0), 1)}%.`,
      `With uncertainty avoidance ${formatNumber(Number(cultural.uncertainty_avoidance || 0), 0)}, copy precision and unit transparency are conversion infrastructure.`,
      `High-severity compliance findings (${formatNumber(Number(compliance.high_severity_findings || 0), 0)}) are growth blockers, not legal side-notes.`,
      `Recommended architecture (${topStrategy}) is the first option in a staged expansion doctrine, not an unconditional rollout mandate.`,
    ];
  }, [data, topStrategy]);

  const chartRows = useMemo(
    () =>
      (decisionRows as DecisionRow[]).map((row) => ({
        strategy: row.strategy,
        scoreMEur: Number(row.risk_adjusted_score || 0) / 1_000_000,
        lossPct: Number(row.weighted_prob_loss || 0) * 100,
      })),
    [decisionRows]
  );

  const scenarios = unique(scenarioRows.map((r) => r.scenario));
  const strategies = unique(scenarioRows.map((r) => r.strategy));

  const matrix = useMemo(() => {
    return scenarios.map((scenario) => {
      const row: Record<string, number | string> = { scenario };
      strategies.forEach((strategy) => {
        const hit = scenarioRows.find((s) => s.scenario === scenario && s.strategy === strategy);
        row[strategy] = hit ? Number(hit.mean_contribution_eur || 0) / 1_000_000 : 0;
      });
      return row;
    });
  }, [scenarioRows, scenarios, strategies]);

  const allValues = matrix.flatMap((r) =>
    strategies.map((s) => Number((r[s] as number) || 0))
  );
  const minVal = allValues.length ? Math.min(...allValues) : 0;
  const maxVal = allValues.length ? Math.max(...allValues) : 0;

  const cellStyle = (value: number) => {
    const span = Math.max(1e-6, maxVal - minVal);
    const norm = (value - minVal) / span;
    const red = Math.round(198 - norm * 170);
    const green = Math.round(40 + norm * 125);
    const blue = Math.round(40 + norm * 90);
    return { backgroundColor: `rgba(${red}, ${green}, ${blue}, 0.24)` };
  };

  if (loading) return <div className="state-box">Loading model payload...</div>;
  if (error) return <div className="state-box error">{error}</div>;

  return (
    <section className="page-block">
      <div className="hero-card">
        <p className="eyebrow">Consulting Team Workspace</p>
        <h1>Executive Strategy Dashboard</h1>
        <p>
          Real-data simulation output for strategic ranking, downside resilience, and stage-gated capital
          decisions.
        </p>
      </div>

      <div className="kpi-grid">
        {kpis.map((kpi) => (
          <article className="kpi-card" key={kpi.label}>
            <div className="kpi-label">{kpi.label}</div>
            <div className="kpi-value">{kpi.value}</div>
          </article>
        ))}
      </div>

      <article className="panel signature-panel">
        <h2>Dr. Ian Helfrich Strategic Lens</h2>
        <p className="panel-subtext">
          Strategy quality comes from disciplined proof architecture: quantified customer value, legal credibility,
          and explicit board triggers for scaling.
        </p>
        <ul className="insight-list">
          {partnerInsights.map((insight) => (
            <li key={insight}>{insight}</li>
          ))}
        </ul>
      </article>

      <div className="panel-grid">
        <article className="panel">
          <h2>Risk-Adjusted Strategy Ranking</h2>
          <div style={{ width: "100%", height: 360 }}>
            <ResponsiveContainer>
              <ComposedChart data={chartRows} margin={{ top: 10, right: 20, left: 8, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="strategy" />
                <YAxis yAxisId="left" label={{ value: "Score (EUR M)", angle: -90, position: "insideLeft" }} />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  label={{ value: "Loss %", angle: -90, position: "insideRight" }}
                />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="scoreMEur" name="Score (EUR M)" fill="#b71c1c" />
                <Line yAxisId="right" dataKey="lossPct" name="Loss Probability (%)" stroke="#111" strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel">
          <h2>Scenario Contribution Matrix (EUR M)</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Scenario</th>
                  {strategies.map((strategy) => (
                    <th key={strategy}>{strategy}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.map((row) => (
                  <tr key={String(row.scenario)}>
                    <td>
                      <strong>{String(row.scenario)}</strong>
                    </td>
                    {strategies.map((strategy) => {
                      const value = Number((row[strategy] as number) || 0);
                      return (
                        <td key={`${row.scenario}-${strategy}`} style={cellStyle(value)}>
                          {formatNumber(value, 2)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article className="panel">
        <h2>Board Gate Triggers</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Gate</th>
                <th>Scale</th>
                <th>Hold</th>
                <th>Redesign</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Weekly pilot contribution</td>
                <td>&gt;= {formatEur(Number(topBaseRow?.p50_contribution_eur || 0), 0)} for 6 weeks</td>
                <td>
                  {formatEur(Number(topBaseRow?.p10_contribution_eur || 0), 0)} to{" "}
                  {formatEur(Number(topBaseRow?.p50_contribution_eur || 0), 0)} with improving trend
                </td>
                <td>&lt; {formatEur(Number(topBaseRow?.p10_contribution_eur || 0), 0)} for 3 weeks</td>
              </tr>
              <tr>
                <td>Compliance severity</td>
                <td>No high-severity findings</td>
                <td>One high-severity finding closed in 14 days</td>
                <td>Two or more unresolved high-severity findings</td>
              </tr>
              <tr>
                <td>Adoption versus model</td>
                <td>&gt;=100% of modeled base adoption</td>
                <td>80-100% of modeled base adoption</td>
                <td>&lt;80% with declining efficiency</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
