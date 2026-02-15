const DATA_PATHS = ["data/presentation_data.json", "./data/presentation_data.json"];

const COLORS = {
  "Wave 1 Pilot": "#b71c1c",
  "Wave 2 Scale": "#ef6c00",
  "Wave 3 Option": "#546e7a",
  Hold: "#8e8e8e",
};

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

const formatPct = (value, digits = 1) =>
  `${(Number(value) * 100).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })}%`;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
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
  throw new Error("Unable to load portfolio data payload.");
}

function populateSelect(select, values, placeholder = "All") {
  select.innerHTML = "";
  const baseOpt = document.createElement("option");
  baseOpt.value = "ALL";
  baseOpt.textContent = placeholder;
  select.appendChild(baseOpt);
  values.forEach((v) => {
    const option = document.createElement("option");
    option.value = v;
    option.textContent = v;
    select.appendChild(option);
  });
}

function buildKpis(rows) {
  const kpi = document.getElementById("kpiRow");
  const wave1 = rows.filter((r) => r.launch_wave === "Wave 1 Pilot").length;
  const goCount = rows.filter((r) => r.board_signal === "GO").length;
  const avgReadiness = rows.length
    ? rows.reduce((acc, r) => acc + Number(r.launch_readiness_score || 0), 0) / rows.length
    : 0;
  const totalExpected = rows
    .filter((r) => r.board_signal !== "NO-GO")
    .reduce((acc, r) => acc + Number(r.expected_contribution_eur || 0), 0);

  const cards = [
    ["Cities Modeled", formatNumber(rows.length, 0)],
    ["Wave 1 Candidates", formatNumber(wave1, 0)],
    ["GO Signals", formatNumber(goCount, 0)],
    ["Expected Portfolio (GO/Cond)", formatEur(totalExpected, 0)],
    ["Average Readiness", `${formatNumber(avgReadiness, 1)}/100`],
  ];

  kpi.innerHTML = cards
    .map(
      ([label, value]) => `
    <article class="kpi">
      <div class="label">${escapeHtml(label)}</div>
      <div class="value">${escapeHtml(value)}</div>
    </article>`
    )
    .join("");
}

function buildTable(rows) {
  const tableWrap = document.getElementById("cityTable");
  const sorted = [...rows].sort((a, b) => Number(a.city_rank) - Number(b.city_rank));
  tableWrap.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>City</th>
          <th>Wave</th>
          <th>Strategy</th>
          <th>Score</th>
          <th>Loss</th>
          <th>Signal</th>
        </tr>
      </thead>
      <tbody>
        ${sorted
          .map((row) => {
            const cls = String(row.board_signal || "").toLowerCase();
            return `<tr>
              <td>${escapeHtml(row.city_rank)}</td>
              <td><strong>${escapeHtml(row.city)}</strong><br><span>${escapeHtml(row.state)}</span></td>
              <td>${escapeHtml(row.launch_wave)}</td>
              <td>${escapeHtml(row.strategy)}</td>
              <td>${escapeHtml(formatEur(row.risk_adjusted_city_score, 0))}</td>
              <td>${escapeHtml(formatPct(row.city_prob_loss, 1))}</td>
              <td><span class="badge ${escapeHtml(cls)}">${escapeHtml(row.board_signal)}</span></td>
            </tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function applyFilters(rows) {
  const wave = document.getElementById("waveFilter").value;
  const strategy = document.getElementById("strategyFilter").value;
  const signal = document.getElementById("signalFilter").value;

  return rows.filter((r) => {
    if (wave !== "ALL" && r.launch_wave !== wave) return false;
    if (strategy !== "ALL" && r.strategy !== strategy) return false;
    if (signal !== "ALL" && r.board_signal !== signal) return false;
    return true;
  });
}

function markerRadius(score, minScore, maxScore) {
  const span = Math.max(1, maxScore - minScore);
  const norm = (score - minScore) / span;
  return 7 + norm * 11;
}

function drawMap(map, rows) {
  if (!rows.length) return;
  const scores = rows.map((r) => Number(r.risk_adjusted_city_score || 0));
  const minScore = Math.min(...scores);
  const maxScore = Math.max(...scores);

  rows.forEach((row) => {
    const color = COLORS[row.launch_wave] || "#8e8e8e";
    const radius = markerRadius(Number(row.risk_adjusted_city_score || 0), minScore, maxScore);

    const marker = L.circleMarker([Number(row.lat), Number(row.lon)], {
      radius,
      color,
      weight: 1.5,
      fillColor: color,
      fillOpacity: 0.65,
    });

    const popup = `
      <div style="font-family: Manrope, sans-serif; font-size: 12px; min-width: 220px;">
        <strong>${escapeHtml(row.city)}</strong> (${escapeHtml(row.state)})<br>
        Wave: ${escapeHtml(row.launch_wave)}<br>
        Strategy: ${escapeHtml(row.strategy)}<br>
        Risk-adjusted score: ${escapeHtml(formatEur(row.risk_adjusted_city_score, 0))}<br>
        Expected contribution: ${escapeHtml(formatEur(row.expected_contribution_eur, 0))}<br>
        Loss probability: ${escapeHtml(formatPct(row.city_prob_loss, 1))}<br>
        Break-even monthly: ${escapeHtml(formatEur(row.adjusted_break_even_monthly_eur, 1))}<br>
        Readiness: ${escapeHtml(formatNumber(row.launch_readiness_score, 1))}/100<br>
        Board signal: <strong>${escapeHtml(row.board_signal)}</strong>
      </div>
    `;
    marker.bindPopup(popup);
    marker.addTo(map);
  });
}

async function init() {
  const btn = document.getElementById("printButton");
  if (btn) btn.addEventListener("click", () => window.print());

  const map = L.map("map", { zoomControl: true }).setView([51.1657, 10.4515], 5.8);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  try {
    const payload = await loadData();
    const cityRows = payload.city_portfolio_plan || payload.city_recommendations || [];

    if (!cityRows.length) {
      throw new Error("No city portfolio data found. Run scenario_runner.py first.");
    }

    const waves = [...new Set(cityRows.map((r) => r.launch_wave))].sort();
    const strategies = [...new Set(cityRows.map((r) => r.strategy))].sort();
    const signals = [...new Set(cityRows.map((r) => r.board_signal))].sort();

    populateSelect(document.getElementById("waveFilter"), waves, "All Waves");
    populateSelect(document.getElementById("strategyFilter"), strategies, "All Strategies");
    populateSelect(document.getElementById("signalFilter"), signals, "All Signals");

    const refresh = () => {
      const filtered = applyFilters(cityRows);
      map.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) map.removeLayer(layer);
      });
      drawMap(map, filtered);
      buildTable(filtered);
      buildKpis(filtered);
    };

    ["waveFilter", "strategyFilter", "signalFilter"].forEach((id) => {
      document.getElementById(id).addEventListener("change", refresh);
    });

    refresh();
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    const side = document.getElementById("cityTable");
    side.innerHTML = `<div style="padding:12px;">${escapeHtml(error.message)}</div>`;
  }
}

init();
