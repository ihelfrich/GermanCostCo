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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const asNum = (value, fallback = 0) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
};

function getScenarioRow(rows, scenario, strategy) {
  return (rows || []).find((r) => r.scenario === scenario && r.strategy === strategy);
}

function getDecisionRow(rows, strategy) {
  return (rows || []).find((r) => r.strategy === strategy);
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
      // fallback path
    }
  }
  throw new Error("Unable to load presentation payload.");
}

function renderTable(targetId, rows, cols) {
  const target = document.getElementById(targetId);
  if (!rows?.length) {
    target.innerHTML = "<p>No data available.</p>";
    return;
  }

  const head = cols.map((c) => `<th>${escapeHtml(c.label)}</th>`).join("");
  const body = rows
    .map((row) => {
      const tds = cols
        .map((c) => {
          const raw = row[c.key];
          const value = c.format ? c.format(raw) : raw;
          return `<td>${escapeHtml(value)}</td>`;
        })
        .join("");
      return `<tr>${tds}</tr>`;
    })
    .join("");

  target.innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function renderSummary(payload) {
  const meta = payload.meta || {};
  const exec = payload.executive_summary || {};
  const decision = payload.key_decision || {};

  document.getElementById("paperTitle").textContent = meta.model_name || "Costco Germany 2026 Market Entry Simulation";
  document.getElementById(
    "paperMeta"
  ).textContent = `Version ${meta.version || "-"} | As of ${meta.as_of_date || "-"} | Generated ${(meta.generated_at_utc || "-").replace("T", " ")}`;

  const cards = [
    ["Recommended Strategy", decision.top_strategy || "-"],
    ["Risk-Adjusted Score", formatEur(exec.recommended_strategy_risk_adjusted_score || 0, 0)],
    ["Top 5Y NPV", formatEur(exec.recommended_strategy_npv_5y_eur || 0, 0)],
    ["Base Standard Fee Loss Prob.", formatPct(exec.base_standard_prob_loss || 0, 1)],
  ];

  const target = document.getElementById("summaryCards");
  target.innerHTML = cards
    .map(([label, value]) => {
      const bad = String(value).includes("-") ? "bad" : "";
      return `
      <article class="summary-card">
        <div class="summary-label">${escapeHtml(label)}</div>
        <div class="summary-value ${bad}">${escapeHtml(value)}</div>
      </article>
    `;
    })
    .join("");

  const thesis =
    "Costco's Germany challenge is not demand absence but model mismatch: when consumer uncertainty is high, value propositions must reduce fee friction, increase informational certainty, and preserve regulatory trust simultaneously.";
  document.getElementById("thesisLine").textContent = thesis;
}

function renderDiscussion(payload) {
  const exec = payload.executive_summary || {};
  const scenarioRows = payload.scenario_summary || [];
  const decisionRows = payload.decision_matrix || [];
  const breakEvenRows = payload.break_even_grid || [];
  const marketingRows = payload.marketing_audit || [];
  const topStrategy = payload?.key_decision?.top_strategy || "subsidized_65_to_20";

  const standardBase = asNum(getScenarioRow(scenarioRows, "base_case", "standard_65")?.mean_contribution_eur);
  const entryBase = asNum(getScenarioRow(scenarioRows, "base_case", "entry_35")?.mean_contribution_eur);
  const topBase = asNum(getScenarioRow(scenarioRows, "base_case", topStrategy)?.mean_contribution_eur);
  const standardDownside = asNum(getScenarioRow(scenarioRows, "downside_stress", "standard_65")?.mean_contribution_eur);
  const topDownside = asNum(getScenarioRow(scenarioRows, "downside_stress", topStrategy)?.mean_contribution_eur);

  const standardLoss = asNum(getDecisionRow(decisionRows, "standard_65")?.weighted_prob_loss);
  const topLoss = asNum(getDecisionRow(decisionRows, topStrategy)?.weighted_prob_loss);

  const feeStepUplift = entryBase - standardBase;
  const fullUplift = topBase - standardBase;
  const stressDeltaTop = topDownside - topBase;
  const stressDeltaStandard = standardDownside - standardBase;

  const breakEvenAbove200 =
    breakEvenRows.length > 0
      ? breakEvenRows.filter((r) => asNum(r.break_even_monthly_spend_eur) > 200).length / breakEvenRows.length
      : 0;

  const marketingRejects = marketingRows.filter((r) => String(r.decision || "").toUpperCase() !== "CONSIDER").length;
  const marketingRejectRate = marketingRows.length > 0 ? marketingRejects / marketingRows.length : 0;

  const compliance = exec.compliance_summary || {};
  const refreshOk = asNum(exec.refresh_ok_sources, 0);
  const refreshTotal = asNum(exec.refresh_total_sources, 0);
  const refreshRatio = refreshTotal > 0 ? refreshOk / refreshTotal : 0;

  const cards = [
    {
      kicker: "Mechanism 1",
      title: "Fee Friction Dominates Base-Case Economics",
      body: `Moving from standard fee to entry fee lifts base-case contribution by ${formatEur(feeStepUplift, 0)}. The full subsidized design lifts it by ${formatEur(fullUplift, 0)}. This is a structural response to household liquidity caution, not a marginal marketing effect.`,
    },
    {
      kicker: "Mechanism 2",
      title: "Risk Is Highly Asymmetric Across Strategies",
      body: `Weighted loss probability is ${formatPct(standardLoss, 1)} for standard fee versus ${formatPct(topLoss, 1)} for the recommended strategy. Tail risk is strategy-made: the wrong fee architecture manufactures downside.`,
    },
    {
      kicker: "Mechanism 3",
      title: "Stress Regime Reveals A Counter-Cyclical Dynamic",
      body: `Under downside stress, recommended-strategy contribution changes by ${formatEur(stressDeltaTop, 0)} from base, while standard fee changes by ${formatEur(stressDeltaStandard, 0)}. This suggests defensive willingness to join when upfront value is explicit.`,
    },
    {
      kicker: "Mechanism 4",
      title: "Capital Constraint, Not Commercial Potential, Blocks Scale",
      body: `Operational scorecards pick ${topStrategy}, but 5-year NPV remains ${formatEur(exec.recommended_strategy_npv_5y_eur || 0, 0)}. The decision boundary is therefore sequencing and option value, not immediate national rollout.`,
    },
    {
      kicker: "Mechanism 5",
      title: "Conversion and Compliance Are Linked Systems",
      body: `${formatPct(marketingRejectRate, 0)} of tested copy variants failed the cue-density threshold, and high-severity compliance findings are ${formatNumber(compliance.high_severity_findings || 0, 0)}. Creative quality and legal quality are one integrated go-to-market control loop.`,
    },
    {
      kicker: "Mechanism 6",
      title: "Model Confidence Is Directionally Strong, Not Fully Mature",
      body: `Automated source refresh passed ${formatNumber(refreshOk, 0)}/${formatNumber(refreshTotal, 0)} inputs (${formatPct(refreshRatio, 0)}). Directional strategy conclusions are stable, but precision claims should be gated until parser coverage rises.`,
    },
  ];

  const target = document.getElementById("discussionGrid");
  target.innerHTML = cards
    .map(
      (card) => `
      <article class="discussion-card">
        <p class="discussion-kicker">${escapeHtml(card.kicker)}</p>
        <h3>${escapeHtml(card.title)}</h3>
        <p>${escapeHtml(card.body)}</p>
      </article>
    `
    )
    .join("");

  const beTarget = breakEvenRows.length ? formatPct(breakEvenAbove200, 1) : "-";
  if (beTarget !== "-") {
    const note = document.createElement("p");
    note.className = "paper-meta";
    note.textContent = `Break-even stress note: ${beTarget} of tested fee/discount combinations require more than EUR 200 monthly spend to break even.`;
    target.insertAdjacentElement("afterend", note);
  }
}

function renderBoardArgument(payload) {
  const scenarioRows = payload.scenario_summary || [];
  const valuationRows = payload.valuation_summary || [];
  const topStrategy = payload?.key_decision?.top_strategy || "subsidized_65_to_20";
  const topBase = asNum(getScenarioRow(scenarioRows, "base_case", topStrategy)?.mean_contribution_eur);
  const topUpside = asNum(getScenarioRow(scenarioRows, "upside_recovery", topStrategy)?.mean_contribution_eur);
  const topDownside = asNum(getScenarioRow(scenarioRows, "downside_stress", topStrategy)?.mean_contribution_eur);
  const topNpv = asNum(valuationRows.find((r) => r.strategy === topStrategy)?.npv_5y_eur);

  const p1 = `The model's key result is a strategic paradox: the recommended design (${topStrategy}) produces robust operating contribution in base (${formatEur(topBase, 0)}), downside (${formatEur(topDownside, 0)}), and upside (${formatEur(topUpside, 0)}) regimes, yet still fails capital screening at ${formatEur(topNpv, 0)} 5-year NPV.`;

  const p2 =
    "The implication is that management should not ask whether Germany is attractive in principle; it should ask whether sequencing, density, and capital pacing can convert operating resilience into investment-grade returns. This is a real-options problem, not a binary market-entry problem.";

  const p3 =
    "Board logic should therefore be: authorize a tightly instrumented pilot, enforce non-negotiable compliance and information-density gates, and treat expansion as contingent on observed elasticity and NPV trajectory improvements. Strategy quality will come from disciplined falsification, not optimism.";

  const target = document.getElementById("boardArgument");
  target.innerHTML = `<p>${escapeHtml(p1)}</p><p>${escapeHtml(p2)}</p><p>${escapeHtml(p3)}</p>`;
}

function renderStrategicEssay(payload) {
  const topStrategy = payload?.key_decision?.top_strategy || "subsidized_65_to_20";
  const exec = payload.executive_summary || {};
  const scenarioRows = payload.scenario_summary || [];
  const decisionRows = payload.decision_matrix || [];
  const financial = payload.financial_assumptions || {};
  const macro = payload.macro || {};

  const standardBase = asNum(getScenarioRow(scenarioRows, "base_case", "standard_65")?.mean_contribution_eur);
  const topBase = asNum(getScenarioRow(scenarioRows, "base_case", topStrategy)?.mean_contribution_eur);
  const topDown = asNum(getScenarioRow(scenarioRows, "downside_stress", topStrategy)?.mean_contribution_eur);
  const topUp = asNum(getScenarioRow(scenarioRows, "upside_recovery", topStrategy)?.mean_contribution_eur);
  const standardLoss = asNum(getDecisionRow(decisionRows, "standard_65")?.weighted_prob_loss);
  const topLoss = asNum(getDecisionRow(decisionRows, topStrategy)?.weighted_prob_loss);
  const wacc = asNum(financial.wacc_percent, 0);
  const climate = asNum(macro.consumer_climate_index, 0);
  const savings = asNum(macro.savings_rate_percent, 0);
  const npv = asNum(exec.recommended_strategy_npv_5y_eur, 0);

  const paragraphs = [
    `Germany entry is best understood as a model-translation problem, not a simple geographic expansion. The U.S. Costco formula assumes that households accept an upfront fee in exchange for latent basket savings. In the modeled German context, consumer climate (${formatNumber(climate, 1)}) and elevated savings behavior (${formatNumber(savings, 1)}%) shift household utility toward certainty and immediate value proof. The strategic question therefore becomes: how much of Costco's existing economic engine can be preserved while redesigning the friction points that this market penalizes.`,
    `The model's strongest commercial finding is structural, not cosmetic. In base conditions, standard-fee economics underperform at ${formatEur(standardBase, 0)}, while the recommended architecture moves contribution to ${formatEur(topBase, 0)}. That is not a marginal uplift; it is a regime shift in economic viability. This indicates that fee architecture carries more explanatory power than campaign optimization for early conversion outcomes.`,
    `Risk diagnostics reinforce the same conclusion. Weighted loss probability falls from ${formatPct(standardLoss, 1)} under standard pricing to ${formatPct(topLoss, 1)} under the recommended strategy. Under downside stress, the recommended strategy still delivers ${formatEur(topDown, 0)} mean contribution and improves further in upside to ${formatEur(topUp, 0)}. In other words, the strategy is not merely optimistic; it is comparatively robust across adverse and favorable states.`,
    `Yet the capital lens imposes discipline. With WACC at ${formatNumber(wacc, 1)}% and current rollout assumptions, the recommended design still produces ${formatEur(npv, 0)} in 5-year NPV. This is the central paradox: operations look resilient while enterprise value creation remains constrained. The correct board response is not to abandon the market, but to stage capital in a way that buys information before committing scale.`,
    `That leads to a falsifiable strategy doctrine: run a controlled pilot, force every launch component through evidence gates, and treat expansion as an earned right rather than a pre-committed plan. If pilot telemetry fails to validate elasticity, compliance reliability, and contribution corridors, the thesis should be revised or halted. This is how rigorous strategy separates conviction from narrative and converts uncertainty into decision quality.`,
  ];

  const target = document.getElementById("strategicEssay");
  target.innerHTML = paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join("");
}

function renderRobustness(payload) {
  const scenarioRows = payload.scenario_summary || [];
  const decisionRows = payload.decision_matrix || [];
  const valuationRows = payload.valuation_summary || [];
  const topStrategy = payload?.key_decision?.top_strategy || "subsidized_65_to_20";

  const standardBase = asNum(getScenarioRow(scenarioRows, "base_case", "standard_65")?.mean_contribution_eur);
  const entryBase = asNum(getScenarioRow(scenarioRows, "base_case", "entry_35")?.mean_contribution_eur);
  const topBase = asNum(getScenarioRow(scenarioRows, "base_case", topStrategy)?.mean_contribution_eur);
  const topDown = asNum(getScenarioRow(scenarioRows, "downside_stress", topStrategy)?.mean_contribution_eur);

  const standardLoss = asNum(getDecisionRow(decisionRows, "standard_65")?.weighted_prob_loss);
  const topLoss = asNum(getDecisionRow(decisionRows, topStrategy)?.weighted_prob_loss);
  const topNpv = asNum(valuationRows.find((r) => r.strategy === topStrategy)?.npv_5y_eur);

  const tests = [
    {
      test: "Fee Architecture Shock",
      observation: `Base-case standard->entry delta: ${formatEur(entryBase - standardBase, 0)}; standard->${topStrategy}: ${formatEur(topBase - standardBase, 0)}.`,
      implication: "Demand response is nonlinear to upfront fee burden; membership design is primary lever.",
    },
    {
      test: "Downside Stress Resilience",
      observation: `${topStrategy} downside-base delta: ${formatEur(topDown - topBase, 0)}.`,
      implication: "Recommended design is not merely a recovery bet; it behaves defensively under stress in this model.",
    },
    {
      test: "Tail-Risk Separation",
      observation: `Weighted loss probability: standard ${formatPct(standardLoss, 1)} vs ${topStrategy} ${formatPct(topLoss, 1)}.`,
      implication: "Tail exposure is management-controllable through strategic design choices.",
    },
    {
      test: "Capital Sufficiency",
      observation: `Top-strategy 5Y NPV: ${formatEur(topNpv, 0)}.`,
      implication: "Scale decision remains financially gated despite favorable operating contribution.",
    },
  ];

  renderTable("robustnessTable", tests, [
    { key: "test", label: "Test" },
    { key: "observation", label: "Observation" },
    { key: "implication", label: "Strategic Implication" },
  ]);
}

function renderDecisionFalsifiers(payload) {
  const topStrategy = payload?.key_decision?.top_strategy || "subsidized_65_to_20";
  const steps = [
    `If ${topStrategy} pilot contribution is below modeled P10 corridor for three consecutive reporting weeks, expansion thesis is invalidated.`,
    "If observed acquisition economics require sustained subsidy without corresponding basket uplift, fee-based moat assumptions are invalidated.",
    "If compliance exceptions remain above threshold after control rollout, speed-to-scale assumptions are invalidated.",
    "If updated 5-year NPV remains negative after pilot recalibration and capex resequencing, national rollout case should be withdrawn.",
  ];
  document.getElementById("decisionFalsifiers").innerHTML = steps.map((s) => `<li>${escapeHtml(s)}</li>`).join("");
}

function renderRecommendations(payload) {
  const stageGated = Boolean(payload?.key_decision?.is_stage_gated);
  const target = document.getElementById("recommendations");

  const steps = stageGated
    ? [
        "Approve a limited-city pilot under a subsidized membership architecture and prohibit immediate national rollout capex.",
        "Deploy a model-to-field control tower: weekly elasticity re-estimation, scenario tracking, and trigger-based intervention playbooks.",
        "Treat legal compliance, marketing information density, and workforce governance as hard launch gates rather than post-launch clean-up.",
        "Authorize phase-2 expansion only after risk-adjusted returns and NPV trend cross board-defined thresholds.",
      ]
    : [
        "Proceed with controlled rollout and weekly scenario tracking.",
        "Maintain compliance and marketing quality gates during scaling.",
      ];

  target.innerHTML = steps.map((s) => `<li>${escapeHtml(s)}</li>`).join("");
}

function renderResearchAgenda(payload) {
  const refreshOk = asNum(payload?.executive_summary?.refresh_ok_sources);
  const refreshTotal = asNum(payload?.executive_summary?.refresh_total_sources);

  const items = [
    "Estimate city-level elasticities from pilot microdata and replace current global priors with hierarchical Bayesian updates.",
    "Integrate competitor reaction functions (price and promotion intensity) using observed Aldi/Lidl/Edeka local responses.",
    "Add working-capital dynamics and cannibalization effects for a fuller capital-allocation view.",
    `Raise automated data-refresh quality from ${formatNumber(refreshOk, 0)}/${formatNumber(refreshTotal, 0)} passing sources to production reliability before external publication.`,
  ];

  document.getElementById("researchAgenda").innerHTML = items.map((s) => `<li>${escapeHtml(s)}</li>`).join("");
}

function renderVisuals(paths) {
  const target = document.getElementById("visualGrid");
  const selected = (paths || []).slice(0, 6);
  target.innerHTML = selected
    .map((path) => {
      const name = path.split("/").pop().replace(".png", "").replaceAll("_", " ");
      return `
      <figure class="visual-card">
        <img src="../${escapeHtml(path)}" alt="${escapeHtml(name)}" loading="lazy" />
        <figcaption>${escapeHtml(name)}</figcaption>
      </figure>
    `;
    })
    .join("");
}

async function init() {
  const printButton = document.getElementById("printButton");
  if (printButton) {
    printButton.addEventListener("click", () => window.print());
  }

  try {
    const payload = await loadData();
    renderSummary(payload);
    renderDiscussion(payload);
    renderBoardArgument(payload);
    renderStrategicEssay(payload);
    renderRobustness(payload);
    renderDecisionFalsifiers(payload);

    renderTable("scenarioTable", payload.scenario_summary || [], [
      { key: "scenario", label: "Scenario" },
      { key: "strategy", label: "Strategy" },
      { key: "mean_contribution_eur", label: "Mean Contribution", format: (v) => formatEur(v, 0) },
      { key: "p10_contribution_eur", label: "P10", format: (v) => formatEur(v, 0) },
      { key: "p90_contribution_eur", label: "P90", format: (v) => formatEur(v, 0) },
      { key: "prob_loss", label: "Loss Prob", format: (v) => formatPct(v, 1) },
      { key: "mean_adoption_rate", label: "Adoption", format: (v) => formatPct(v, 1) },
    ]);

    renderTable("decisionTable", payload.decision_matrix || [], [
      { key: "rank", label: "Rank", format: (v) => formatNumber(v, 0) },
      { key: "strategy", label: "Strategy" },
      { key: "weighted_mean_contribution_eur", label: "Weighted Mean", format: (v) => formatEur(v, 0) },
      { key: "weighted_prob_loss", label: "Weighted Loss", format: (v) => formatPct(v, 1) },
      { key: "risk_adjusted_score", label: "Risk-Adjusted", format: (v) => formatEur(v, 0) },
    ]);

    renderTable("valuationTable", payload.valuation_summary || [], [
      { key: "strategy", label: "Strategy" },
      { key: "npv_5y_eur", label: "5Y NPV", format: (v) => formatEur(v, 0) },
      { key: "payback_year", label: "Payback Year", format: (v) => (asNum(v, -1) < 0 ? "No payback" : formatNumber(v, 0)) },
    ]);

    const sourceRows = Object.entries(payload.sources || {}).map(([id, source]) => ({ id, ...source }));
    renderTable("sourceTable", sourceRows, [
      { key: "id", label: "ID" },
      { key: "source", label: "Source" },
      { key: "evidence", label: "Evidence" },
      { key: "url", label: "URL" },
    ]);

    renderRecommendations(payload);
    renderResearchAgenda(payload);
    renderVisuals(payload.chart_paths || []);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    document.getElementById("paperRoot").innerHTML = `
      <section class="paper-section">
        <h2>Load Error</h2>
        <p>Unable to load payload. Run <code>python3 scripts/build_presentation_data.py</code> and refresh.</p>
      </section>
    `;
  }
}

init();
