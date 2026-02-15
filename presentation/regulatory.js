const DATA_PATHS = ["data/presentation_data.json", "./data/presentation_data.json"];

const formatNumber = (value, digits = 0) =>
  Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });

const formatEur = (value, digits = 0) =>
  `EUR ${Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}`;

const plotLayoutBase = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Manrope, sans-serif", color: "#151515" },
  margin: { l: 58, r: 20, t: 12, b: 48 },
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function severityClass(score) {
  if (Number(score) >= 5) return "high";
  if (Number(score) >= 3) return "medium";
  return "low";
}

function parseDate(value) {
  if (!value) return null;
  const ts = Date.parse(String(value));
  return Number.isNaN(ts) ? null : new Date(ts);
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
      // continue
    }
  }
  throw new Error("Unable to load presentation payload.");
}

function renderMeta(payload, rows) {
  const meta = payload.meta || {};
  const line = document.getElementById("metaLine");
  line.textContent = `${rows.length} obligations mapped | payload ${
    (meta.generated_at_utc || "").replace("T", " ").replace("Z", " UTC") || "-"
  }`;
}

function renderKpis(payload, rows) {
  const summary = payload.regulatory_summary || {};
  const due2026 = rows.filter((r) => {
    const dt = parseDate(r.effective_date);
    return dt && dt >= new Date("2026-01-01") && dt <= new Date("2026-12-31");
  }).length;

  const cards = [
    ["Mapped Obligations", formatNumber(summary.count_total || rows.length, 0)],
    ["High-Severity Items", formatNumber(summary.count_high_severity || 0, 0)],
    ["2026 Effective Items", formatNumber(due2026, 0)],
    ["Near-Term (2026-2027)", formatNumber(summary.near_term_2026_2027 || 0, 0)],
    ["Largest Explicit Fine", formatEur(summary.max_explicit_fine_eur || 0, 0)],
  ];

  const kpiRow = document.getElementById("kpiRow");
  kpiRow.innerHTML = cards
    .map(
      ([label, value]) => `
      <article class="kpi">
        <div class="label">${escapeHtml(label)}</div>
        <div class="value">${escapeHtml(value)}</div>
      </article>`
    )
    .join("");
}

function renderTimeline(rows) {
  const usable = rows
    .map((r) => ({ ...r, dateObj: parseDate(r.effective_date) }))
    .filter((r) => r.dateObj)
    .sort((a, b) => a.dateObj - b.dateObj);

  const trace = {
    x: usable.map((r) => r.effective_date),
    y: usable.map((r) => r.category),
    text: usable.map((r) => r.regulation),
    mode: "markers+text",
    textposition: "top center",
    marker: {
      size: usable.map((r) => 8 + Number(r.likelihood_score_1_to_5 || 1) * 3),
      color: usable.map((r) => Number(r.severity_score_1_to_5 || 1)),
      colorscale: [
        [0, "#a8c8a0"],
        [0.5, "#d9c598"],
        [1, "#b71c1c"],
      ],
      cmin: 1,
      cmax: 5,
      colorbar: { title: "Severity" },
      line: { color: "#2b2b2b", width: 0.8 },
      opacity: 0.85,
    },
    hovertemplate:
      "<b>%{text}</b><br>Date: %{x}<br>Category: %{y}<extra></extra>",
    type: "scatter",
  };

  const layout = {
    ...plotLayoutBase,
    xaxis: { title: "Effective Date", tickformat: "%Y-%m-%d", showgrid: true },
    yaxis: { title: "Domain", showgrid: true },
  };

  Plotly.newPlot("timelineChart", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderRiskMatrix(rows) {
  const trace = {
    x: rows.map((r) => Number(r.likelihood_score_1_to_5 || 1)),
    y: rows.map((r) => Number(r.severity_score_1_to_5 || 1)),
    text: rows.map((r) => `${r.category}: ${r.regulation}`),
    mode: "markers",
    marker: {
      size: rows.map((r) => 10 + Number(r.severity_score_1_to_5 || 1) * 2),
      color: rows.map((r) => Number(r.severity_score_1_to_5 || 1)),
      colorscale: [
        [0, "#cde2c7"],
        [0.5, "#f0ddae"],
        [1, "#c62828"],
      ],
      cmin: 1,
      cmax: 5,
      line: { width: 0.8, color: "#333" },
      opacity: 0.85,
    },
    hovertemplate: "%{text}<br>Likelihood: %{x}<br>Severity: %{y}<extra></extra>",
    type: "scatter",
  };

  const layout = {
    ...plotLayoutBase,
    xaxis: { title: "Likelihood (1-5)", dtick: 1, range: [0.5, 5.5] },
    yaxis: { title: "Severity (1-5)", dtick: 1, range: [0.5, 5.5] },
    shapes: [
      {
        type: "rect",
        x0: 3.5,
        x1: 5.5,
        y0: 3.5,
        y1: 5.5,
        line: { width: 0 },
        fillcolor: "rgba(183, 28, 28, 0.08)",
      },
    ],
  };

  Plotly.newPlot("riskMatrixChart", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderOwnerChart(rows) {
  const counts = {};
  rows.forEach((r) => {
    const owner = r.operational_owner || "Unknown";
    counts[owner] = (counts[owner] || 0) + 1;
  });

  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const trace = {
    x: entries.map((x) => x[0]),
    y: entries.map((x) => x[1]),
    type: "bar",
    marker: { color: "#6e6e6e" },
    hovertemplate: "%{x}<br>Obligations: %{y}<extra></extra>",
  };

  const layout = {
    ...plotLayoutBase,
    yaxis: { title: "Count of obligations", dtick: 1 },
    xaxis: { title: "Control owner" },
  };

  Plotly.newPlot("ownerChart", [trace], layout, { displayModeBar: false, responsive: true });
}

function renderPlaybook(rows) {
  const grouped = {};
  rows.forEach((r) => {
    const owner = r.operational_owner || "Unknown";
    if (!grouped[owner]) {
      grouped[owner] = [];
    }
    grouped[owner].push(r);
  });

  const ownerRows = Object.entries(grouped)
    .map(([owner, items]) => {
      const sorted = [...items].sort(
        (a, b) =>
          Number(b.severity_score_1_to_5 || 0) - Number(a.severity_score_1_to_5 || 0)
      );
      const top = sorted[0];
      return {
        owner,
        obligations: items.length,
        topRisk: top.regulation,
        controlAction: top.requirement,
        maxSanction: top.maximum_sanction,
      };
    })
    .sort((a, b) => b.obligations - a.obligations);

  const head = `
    <tr>
      <th>Owner</th>
      <th>Obligations</th>
      <th>Priority Regulation</th>
      <th>Immediate Control Requirement</th>
      <th>Sanction Envelope</th>
    </tr>`;
  const body = ownerRows
    .map(
      (r) => `
      <tr>
        <td><strong>${escapeHtml(r.owner)}</strong></td>
        <td>${escapeHtml(formatNumber(r.obligations, 0))}</td>
        <td>${escapeHtml(r.topRisk)}</td>
        <td>${escapeHtml(r.controlAction)}</td>
        <td>${escapeHtml(r.maxSanction)}</td>
      </tr>`
    )
    .join("");

  document.getElementById("playbookTable").innerHTML = `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

function renderRegister(rows) {
  const sorted = [...rows].sort((a, b) => {
    const sev = Number(b.severity_score_1_to_5 || 0) - Number(a.severity_score_1_to_5 || 0);
    if (sev !== 0) return sev;
    const ad = parseDate(a.effective_date);
    const bd = parseDate(b.effective_date);
    return (ad ? ad.getTime() : 0) - (bd ? bd.getTime() : 0);
  });

  const head = `
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
    </tr>`;

  const body = sorted
    .map((r) => {
      const sev = Number(r.severity_score_1_to_5 || 0);
      const sevPill = `<span class="pill ${severityClass(sev)}">${formatNumber(sev, 0)}</span>`;
      return `
        <tr>
          <td>${escapeHtml(r.effective_date || "-")}</td>
          <td>${escapeHtml(r.category || "-")}</td>
          <td><strong>${escapeHtml(r.regulation || "-")}</strong><br>${escapeHtml(
            r.deadline_or_trigger || ""
          )}</td>
          <td>${escapeHtml(r.requirement || "-")}</td>
          <td>${escapeHtml(r.maximum_sanction || "-")}</td>
          <td>${sevPill}</td>
          <td>${escapeHtml(formatNumber(r.likelihood_score_1_to_5 || 0, 0))}</td>
          <td>${escapeHtml(r.operational_owner || "-")}</td>
          <td><a class="source-link" href="${escapeHtml(r.source_url || "#")}" target="_blank" rel="noopener noreferrer">Source</a><br>${escapeHtml(
            r.source_note || ""
          )}</td>
        </tr>`;
    })
    .join("");

  document.getElementById("registerTable").innerHTML = `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

async function init() {
  const printButton = document.getElementById("printButton");
  if (printButton) {
    printButton.addEventListener("click", () => window.print());
  }

  try {
    const payload = await loadData();
    const rows = payload.regulatory_environment || [];
    if (!rows.length) {
      throw new Error("No regulatory data in payload. Run build_presentation_data.py.");
    }

    renderMeta(payload, rows);
    renderKpis(payload, rows);
    renderTimeline(rows);
    renderRiskMatrix(rows);
    renderOwnerChart(rows);
    renderPlaybook(rows);
    renderRegister(rows);
  } catch (err) {
    document.querySelector(".page").innerHTML = `<section class="panel"><h2>Load Error</h2><p>${escapeHtml(
      err.message
    )}</p></section>`;
  }
}

init();
