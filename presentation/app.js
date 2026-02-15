const DATA_PATHS = ["data/presentation_data.json", "./data/presentation_data.json"];

const formatNumber = (value, digits = 0) =>
  Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });

const formatPct = (value, digits = 1) =>
  `${(Number(value) * 100).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}%`;

const formatEur = (value, digits = 0) =>
  `EUR ${Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}`;

const toMillions = (value) => Number(value) / 1e6;

const plotLayoutBase = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  margin: { l: 50, r: 24, t: 12, b: 46 },
  font: { family: "Manrope, sans-serif", color: "#1a1a1a" },
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function updateScrollProgress() {
  const progress = document.getElementById("scrollProgress");
  if (!progress) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const ratio = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  progress.style.width = `${Math.min(100, Math.max(0, ratio))}%`;
}

function observeAnimations() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("in");
      });
    },
    { threshold: 0.12 }
  );
  document.querySelectorAll("[data-animate]").forEach((el) => observer.observe(el));
}

async function loadData() {
  if (typeof window !== "undefined" && window.PRESENTATION_DATA) {
    return window.PRESENTATION_DATA;
  }
  for (const path of DATA_PATHS) {
    try {
      const response = await fetch(path);
      if (response.ok) return response.json();
    } catch (_) {
      // try next path
    }
  }
  throw new Error("Unable to load presentation data payload.");
}

function setMeta(payload) {
  const meta = payload.meta || {};
  const keyDecision = payload.key_decision || {};
  document.getElementById("metaVersion").textContent = `Model v${meta.version || "-"}`;
  document.getElementById("metaAsOf").textContent = meta.as_of_date || "-";
  document.getElementById("metaGenerated").textContent = (meta.generated_at_utc || "-").replace("T", " ").replace("Z", "");
  document.getElementById("metaTopStrategy").textContent = keyDecision.top_strategy || "-";

  const refresh = payload.executive_summary || {};
  const footer = document.getElementById("footerRefreshStatus");
  if (footer) {
    footer.textContent = `Refresh status: ${refresh.refresh_ok_sources ?? 0}/${refresh.refresh_total_sources ?? 0} sources OK`;
  }
}

function renderThesis(payload) {
  const exec = payload.executive_summary || {};
  const decision = payload.key_decision || {};
  const baseLoss = Number(exec.base_standard_prob_loss || 0);
  const npv = Number(exec.recommended_strategy_npv_5y_eur || 0);
  const refreshOk = Number(exec.refresh_ok_sources || 0);
  const refreshTotal = Number(exec.refresh_total_sources || 0);

  const theses = [
    {
      kicker: "Commercial Fit",
      title: "Standard Fee Design Fails in Base Case",
      text: `At EUR 65 equivalent, modeled base-case loss probability is ${formatPct(baseLoss, 1)}. Germany conversion requires fee redesign, not just media optimization.`,
    },
    {
      kicker: "Capital Lens",
      title: "Best Strategy Still Screens Negative on 5Y NPV",
      text: `${escapeHtml(decision.top_strategy || "Top strategy")} leads operational scorecards, yet 5-year NPV is ${formatEur(npv, 0)}. Recommendation is stage-gated pilot with hard expansion triggers.`,
    },
    {
      kicker: "Evidence Health",
      title: "Refresh Pipeline Is Working but Gate-Constrained",
      text: `Automated refresh validated ${refreshOk}/${refreshTotal} sources this run. Keep conservative defaults until parser coverage reaches production threshold.`,
    },
  ];

  const target = document.getElementById("thesisCards");
  target.innerHTML = "";
  theses.forEach((item) => {
    const card = document.createElement("article");
    card.className = "thesis-card";
    card.innerHTML = `
      <div class="thesis-kicker">${escapeHtml(item.kicker)}</div>
      <h3 class="thesis-title">${escapeHtml(item.title)}</h3>
      <p class="thesis-text">${escapeHtml(item.text)}</p>
    `;
    target.appendChild(card);
  });
}

function computeReadiness(payload) {
  const exec = payload.executive_summary || {};
  const compliance = exec.compliance_summary || {};

  let score = 100;
  if (Number(exec.recommended_strategy_npv_5y_eur || 0) < 0) score -= 35;
  score -= Math.min(30, Number(exec.base_standard_prob_loss || 0) * 30);
  score -= Math.min(21, Number(compliance.high_severity_findings || 0) * 7);

  const ok = Number(exec.refresh_ok_sources || 0);
  const total = Number(exec.refresh_total_sources || 0);
  const refreshRatio = total > 0 ? ok / total : 0;
  if (refreshRatio < 0.6) score -= 10;

  score = Math.max(0, Math.min(100, score));

  let status = "Go";
  let cls = "go";
  if (score < 75) {
    status = "Hold / Pilot";
    cls = "hold";
  }
  if (score < 50) {
    status = "No-Go / Redesign";
    cls = "stop";
  }

  return {
    score,
    status,
    cls,
    drivers: [
      `High-severity compliance findings: ${formatNumber(compliance.high_severity_findings || 0, 0)}`,
      `Base standard-fee loss probability: ${formatPct(exec.base_standard_prob_loss || 0, 1)}`,
      `Top strategy 5Y NPV: ${formatEur(exec.recommended_strategy_npv_5y_eur || 0, 0)}`,
      `Refresh confidence: ${formatNumber(ok, 0)}/${formatNumber(total, 0)} sources`,
    ],
  };
}

function renderReadiness(payload) {
  const readiness = computeReadiness(payload);
  const target = document.getElementById("readinessPanel");
  target.innerHTML = `
    <article class="readiness-card">
      <div class="readiness-top">
        <div class="readiness-ring" style="--pct:${readiness.score}">
          <span class="readiness-score">${formatNumber(readiness.score, 0)}</span>
        </div>
        <div>
          <div class="readiness-label">Decision Signal</div>
          <div class="readiness-status ${readiness.cls}">${escapeHtml(readiness.status)}</div>
          <div class="item-body">Composite score across economics, downside risk, compliance, and data reliability.</div>
        </div>
      </div>
      <ul class="readiness-list">
        ${readiness.drivers.map((d) => `<li><strong>Driver:</strong> ${escapeHtml(d)}</li>`).join("")}
      </ul>
    </article>
  `;
}

function renderKpis(payload) {
  const insights = payload.executive_summary || {};
  const decision = payload.key_decision || {};
  const compliance = insights.compliance_summary || {};

  const kpis = [
    ["Recommended Strategy", decision.top_strategy || "-"],
    ["Risk-Adjusted Score", formatNumber(insights.recommended_strategy_risk_adjusted_score || 0, 0)],
    ["5Y NPV (Top Strategy)", formatEur(insights.recommended_strategy_npv_5y_eur || 0, 0)],
    ["Base Std. Loss Probability", formatPct(insights.base_standard_prob_loss || 0, 1)],
    ["Labor Inflation 2026->2027", formatPct((insights.labor_delta_pct || 0) / 100, 2)],
    ["High-Severity Findings", formatNumber(compliance.high_severity_findings || 0, 0)],
    ["Marketing Reject Count", formatNumber(insights.marketing_reject_count || 0, 0)],
    ["Refresh Sources OK", `${insights.refresh_ok_sources || 0}/${insights.refresh_total_sources || 0}`],
  ];

  const grid = document.getElementById("kpiGrid");
  grid.innerHTML = "";
  kpis.forEach(([label, value]) => {
    const card = document.createElement("article");
    card.className = "kpi-card";
    const neg = typeof value === "string" && value.includes("-");
    card.innerHTML = `
      <div class="kpi-label">${escapeHtml(label)}</div>
      <div class="kpi-value ${neg ? "negative" : ""}">${escapeHtml(value)}</div>
    `;
    grid.appendChild(card);
  });
}

function renderDecisionChart(decisionRows) {
  const sorted = [...decisionRows].sort((a, b) => a.rank - b.rank);
  const x = sorted.map((r) => r.strategy);
  const y1 = sorted.map((r) => toMillions(r.risk_adjusted_score));
  const y2 = sorted.map((r) => Number(r.weighted_prob_loss) * 100);

  const traceScore = {
    x,
    y: y1,
    type: "bar",
    name: "Risk-Adjusted Score (EUR M)",
    marker: { color: ["#b71c1c", "#666666", "#9f9f9f"] },
  };

  const traceLoss = {
    x,
    y: y2,
    mode: "lines+markers",
    name: "Weighted Loss Probability (%)",
    yaxis: "y2",
    line: { color: "#111111", width: 2 },
    marker: { size: 7 },
  };

  const layout = {
    ...plotLayoutBase,
    margin: { l: 50, r: 56, t: 12, b: 45 },
    yaxis: { title: "EUR Millions", zeroline: true, zerolinecolor: "#bbb" },
    yaxis2: {
      title: "Loss %",
      overlaying: "y",
      side: "right",
      range: [0, Math.max(100, ...y2) * 1.1],
    },
    legend: { orientation: "h", y: 1.15 },
  };

  Plotly.newPlot("decisionChart", [traceScore, traceLoss], layout, { displayModeBar: false, responsive: true });
}

function renderSimpleTable(targetId, rows, columns) {
  const target = document.getElementById(targetId);
  if (!rows.length) {
    target.innerHTML = "<p>No data available.</p>";
    return;
  }

  const thead = columns.map((c) => `<th>${escapeHtml(c.label)}</th>`).join("");
  const tbody = rows
    .map((row) => {
      const tds = columns
        .map((c) => {
          const raw = row[c.key];
          const val = c.format ? c.format(raw) : raw;
          return `<td>${escapeHtml(val ?? "")}</td>`;
        })
        .join("");
      return `<tr>${tds}</tr>`;
    })
    .join("");

  target.innerHTML = `<table><thead><tr>${thead}</tr></thead><tbody>${tbody}</tbody></table>`;
}

function renderScenarioHeatmap(rows) {
  const scenarios = [...new Set(rows.map((r) => r.scenario))];
  const strategies = [...new Set(rows.map((r) => r.strategy))];
  const z = scenarios.map((scenario) =>
    strategies.map((strategy) => {
      const row = rows.find((r) => r.scenario === scenario && r.strategy === strategy);
      return row ? toMillions(row.mean_contribution_eur) : null;
    })
  );

  const trace = {
    x: strategies,
    y: scenarios,
    z,
    type: "heatmap",
    colorscale: [
      [0, "#c62828"],
      [0.5, "#efefef"],
      [1, "#1b5e20"],
    ],
    zmid: 0,
    hovertemplate: "%{y}<br>%{x}<br>EUR %{z:.2f}M<extra></extra>",
  };

  const layout = {
    ...plotLayoutBase,
    margin: { l: 96, r: 20, t: 12, b: 45 },
  };

  Plotly.newPlot("scenarioHeatmap", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderDownsideChart(rows) {
  const scenarios = [...new Set(rows.map((r) => r.scenario))];
  const strategies = [...new Set(rows.map((r) => r.strategy))];
  const traces = strategies.map((strategy, i) => ({
    x: scenarios,
    y: scenarios.map((scenario) => {
      const row = rows.find((r) => r.scenario === scenario && r.strategy === strategy);
      return row ? Number(row.prob_loss) * 100 : 0;
    }),
    type: "bar",
    name: strategy,
    marker: { color: ["#b71c1c", "#6e6e6e", "#8e8e8e"][i % 3] },
  }));

  const layout = {
    ...plotLayoutBase,
    barmode: "group",
    yaxis: { title: "Loss Probability (%)", range: [0, 105] },
    legend: { orientation: "h", y: 1.15 },
  };

  Plotly.newPlot("downsideChart", traces, layout, { displayModeBar: false, responsive: true });
}

function renderNpvChart(rows) {
  const sorted = [...rows].sort((a, b) => Number(b.npv_5y_eur) - Number(a.npv_5y_eur));
  const trace = {
    x: sorted.map((r) => r.strategy),
    y: sorted.map((r) => toMillions(r.npv_5y_eur)),
    type: "bar",
    marker: {
      color: sorted.map((_, i) => (i === 0 ? "#b71c1c" : "#6e6e6e")),
    },
  };

  const layout = {
    ...plotLayoutBase,
    yaxis: { title: "NPV (EUR Millions)", zeroline: true, zerolinecolor: "#bbb" },
  };

  Plotly.newPlot("npvChart", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderCashflowChart(rows) {
  const strategies = [...new Set(rows.map((r) => r.strategy))];
  const palette = ["#b71c1c", "#555555", "#888888"];
  const traces = strategies.map((strategy, idx) => {
    const subset = rows.filter((r) => r.strategy === strategy).sort((a, b) => Number(a.year) - Number(b.year));
    return {
      x: subset.map((r) => Number(r.year)),
      y: subset.map((r) => toMillions(r.free_cash_flow_eur)),
      mode: "lines+markers",
      name: strategy,
      line: { color: palette[idx % palette.length], width: 2.3 },
      marker: { size: 6 },
    };
  });

  const layout = {
    ...plotLayoutBase,
    xaxis: { title: "Year" },
    yaxis: { title: "FCF (EUR Millions)", zeroline: true, zerolinecolor: "#bbb" },
    legend: { orientation: "h", y: 1.15 },
  };

  Plotly.newPlot("cashflowChart", traces, layout, { displayModeBar: false, responsive: true });
}

function renderBreakEvenChart(rows) {
  if (!rows.length) return;

  const fees = [...new Set(rows.map((r) => Number(r.membership_fee_eur)))].sort((a, b) => a - b);
  const discounts = [...new Set(rows.map((r) => Number(r.bulk_discount)))].sort((a, b) => a - b);

  const z = fees.map((fee) =>
    discounts.map((discount) => {
      const row = rows.find(
        (item) => Number(item.membership_fee_eur) === fee && Math.abs(Number(item.bulk_discount) - discount) < 1e-9
      );
      return row ? Number(row.break_even_monthly_spend_eur) : null;
    })
  );

  const trace = {
    x: discounts.map((d) => d * 100),
    y: fees,
    z,
    type: "contour",
    colorscale: [
      [0, "#1b5e20"],
      [0.5, "#f0f0f0"],
      [1, "#b71c1c"],
    ],
    contours: {
      coloring: "heatmap",
      showlabels: true,
      labelfont: { size: 10, color: "#262626" },
    },
    hovertemplate: "Fee EUR %{y}<br>Discount %{x:.1f}<br>Break-even EUR %{z:.0f}/month<extra></extra>",
    colorbar: { title: "EUR / month" },
  };

  const layout = {
    ...plotLayoutBase,
    xaxis: { title: "Bulk Discount (%)" },
    yaxis: { title: "Membership Fee (EUR)" },
    margin: { l: 62, r: 30, t: 12, b: 50 },
  };

  Plotly.newPlot("breakEvenChart", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderMarketingAudit(rows) {
  const target = document.getElementById("marketingAudit");
  target.innerHTML = "";
  rows.forEach((row) => {
    const cls = row.decision === "CONSIDER" ? "good" : "bad";
    const node = document.createElement("article");
    node.className = "item-card";
    node.innerHTML = `
      <div class="item-header">
        <div class="item-title">Cues: ${formatNumber(row.cue_count, 0)} | Confidence: ${formatNumber(row.confidence_score, 2)}</div>
        <span class="badge ${cls}">${escapeHtml(row.decision)}</span>
      </div>
      <div class="item-body"><strong>Copy:</strong> ${escapeHtml(row.text)}</div>
      <div class="item-body">${escapeHtml(row.reason)}</div>
    `;
    target.appendChild(node);
  });
}

function renderComplianceAudit(green, workforce) {
  const target = document.getElementById("complianceAudit");
  target.innerHTML = "";
  [...green, ...workforce].slice(0, 10).forEach((row) => {
    const status = row.status || "INFO";
    const severity = String(row.severity || "NONE").toUpperCase();
    const cls = status === "PASS" ? "good" : severity === "HIGH" ? "bad" : "warn";

    const title = row.label || row.rule || (row.record ? JSON.stringify(row.record) : "Compliance Item");
    const details = row.reason || row.remediation || (row.alerts ? row.alerts.join(", ") : "");

    const node = document.createElement("article");
    node.className = "item-card";
    node.innerHTML = `
      <div class="item-header">
        <div class="item-title">${escapeHtml(title)}</div>
        <span class="badge ${cls}">${escapeHtml(status)} / ${escapeHtml(severity)}</span>
      </div>
      <div class="item-body">${escapeHtml(details)}</div>
    `;
    target.appendChild(node);
  });
}

function renderSources(sourceMap) {
  const target = document.getElementById("sourceCards");
  target.innerHTML = "";
  Object.entries(sourceMap).forEach(([id, source]) => {
    const node = document.createElement("article");
    node.className = "source-card";
    node.innerHTML = `
      <h4>${escapeHtml(source.source || id)}</h4>
      <p>${escapeHtml(source.evidence || "")}</p>
      <a href="${escapeHtml(source.url || "#")}" target="_blank" rel="noreferrer">Open Source</a>
    `;
    target.appendChild(node);
  });
}

function buildRoadmap(payload) {
  const stageGated = Boolean(payload?.key_decision?.is_stage_gated);
  if (stageGated) {
    return [
      {
        phase: "Phase 1: Pilot Design",
        window: "Q2 2026",
        actions: [
          "Launch 2-city pilot with subsidized fee architecture and strict cohort instrumentation.",
          "Mandate 7+ information cues in all POS and paid-media templates before deployment.",
        ],
      },
      {
        phase: "Phase 2: Control and Calibration",
        window: "Q3 2026",
        actions: [
          "Re-estimate adoption and elasticity using observed household transaction microdata.",
          "Enforce EmpCo-compliant green claims and works-council scheduling protocol audit.",
        ],
      },
      {
        phase: "Phase 3: Investment Gate",
        window: "Q4 2026",
        actions: [
          "Proceed to rollout only if 5Y NPV scenario median is non-negative and CVaR improves.",
          "Freeze expansion and redesign membership ladder if contribution tracks below P10 corridor.",
        ],
      },
    ];
  }

  return [
    {
      phase: "Phase 1: Rollout Prep",
      window: "Q2 2026",
      actions: [
        "Finalize launch cities and marketing playbook.",
        "Stand up compliance and workforce governance controls.",
      ],
    },
    {
      phase: "Phase 2: Controlled Expansion",
      window: "Q3-Q4 2026",
      actions: [
        "Scale by cluster while monitoring downside risk signals weekly.",
        "Tune membership mix by city based on realized break-even behavior.",
      ],
    },
  ];
}

function renderRoadmap(payload) {
  const steps = buildRoadmap(payload);
  const target = document.getElementById("roadmap");
  target.innerHTML = "";
  steps.forEach((step) => {
    const node = document.createElement("article");
    node.className = "roadmap-step";
    node.innerHTML = `
      <div class="roadmap-head">
        <div class="roadmap-phase">${escapeHtml(step.phase)}</div>
        <div class="roadmap-window">${escapeHtml(step.window)}</div>
      </div>
      <ul class="roadmap-actions">
        ${step.actions.map((action) => `<li>${escapeHtml(action)}</li>`).join("")}
      </ul>
    `;
    target.appendChild(node);
  });
}

function renderImageGallery(paths) {
  const target = document.getElementById("imageGallery");
  target.innerHTML = "";
  paths.forEach((path) => {
    const figure = document.createElement("figure");
    figure.className = "img-card";
    const src = `../${path}`;
    const name = path.split("/").pop().replace(".png", "");
    figure.innerHTML = `
      <img src="${escapeHtml(src)}" alt="${escapeHtml(name)}" loading="lazy" />
      <figcaption>${escapeHtml(name.replaceAll("_", " "))}</figcaption>
    `;
    target.appendChild(figure);
  });
}

function bindActions() {
  const btn = document.getElementById("printButton");
  if (btn) {
    btn.addEventListener("click", () => window.print());
  }
  window.addEventListener("scroll", updateScrollProgress);
  updateScrollProgress();
}

async function init() {
  try {
    const payload = await loadData();
    setMeta(payload);
    renderThesis(payload);
    renderKpis(payload);
    renderReadiness(payload);

    const decisionRows = payload.decision_matrix || [];
    renderDecisionChart(decisionRows);
    renderSimpleTable("decisionTable", decisionRows, [
      { key: "rank", label: "Rank", format: (v) => formatNumber(v, 0) },
      { key: "strategy", label: "Strategy" },
      { key: "weighted_mean_contribution_eur", label: "Weighted Mean", format: (v) => formatEur(v, 0) },
      { key: "weighted_prob_loss", label: "Loss Prob", format: (v) => formatPct(v, 1) },
      { key: "weighted_cvar5_contribution_eur", label: "CVaR 5%", format: (v) => formatEur(v, 0) },
      { key: "risk_adjusted_score", label: "Risk Score", format: (v) => formatEur(v, 0) },
    ]);

    const scenarioRows = payload.scenario_summary || [];
    renderScenarioHeatmap(scenarioRows);
    renderDownsideChart(scenarioRows);

    renderNpvChart(payload.valuation_summary || []);
    renderCashflowChart(payload.valuation_cashflows || []);
    renderBreakEvenChart(payload.break_even_grid || []);

    renderMarketingAudit(payload.marketing_audit || []);
    renderComplianceAudit(payload.green_audit || [], payload.workforce_audit || []);
    renderSources(payload.sources || {});
    renderRoadmap(payload);
    renderImageGallery(payload.chart_paths || []);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    document.body.innerHTML = `
      <main style="padding: 2rem; font-family: Manrope, sans-serif;">
        <h1>Presentation Load Error</h1>
        <p>Unable to load presentation data. Run:</p>
        <pre>python3 scripts/build_presentation_data.py</pre>
      </main>
    `;
  }
}

bindActions();
observeAnimations();
init();
