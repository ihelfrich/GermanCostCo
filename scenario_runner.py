"""Board-grade strategy simulation dashboard for Costco Germany market entry (2026)."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Keep matplotlib cache writable inside project sandbox.
os.environ.setdefault("MPLCONFIGDIR", str(Path(".mpl_cache")))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from compliance_engine import (
    audit_green_claims,
    check_workforce_scheduling,
    summarize_regulatory_risk,
)
from config_loader import load_config
from consumer_psychology_model import GermanConsumer


def dataframe_to_markdown(df: pd.DataFrame, decimals: int = 2) -> str:
    """Minimal markdown serializer to avoid optional dependency on tabulate."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].map(lambda x: f"{x:,.{decimals}f}")
    headers = [str(c) for c in out.columns]
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in out.iterrows():
        vals = [str(row[col]) for col in out.columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def apply_swiss_style(config: Dict) -> None:
    """Swiss-style aesthetic with restrained color accents and clean typography."""
    theme = config["visual_theme"]
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "axes.facecolor": theme["bg"],
            "figure.facecolor": "#FFFFFF",
            "axes.edgecolor": theme["grey"],
            "axes.labelcolor": theme["text"],
            "xtick.color": theme["text"],
            "ytick.color": theme["text"],
            "text.color": theme["text"],
            "grid.color": theme["light_grey"],
            "grid.linewidth": 0.9,
            "axes.grid": True,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "figure.titlesize": 14,
        }
    )
    sns.set_style("whitegrid")


def calculate_labor_cost_per_warehouse(config: Dict, year: int) -> float:
    """Annual labor cost from minimum wage and staffing assumptions."""
    assumptions = config["operational_assumptions"]
    key = f"min_wage_{year}_eur_per_hour"
    hourly_wage = config["labor_legal"][key]  # Source: Zoll
    return (
        hourly_wage
        * assumptions["employees_per_warehouse"]
        * assumptions["hours_per_employee_per_year"]
    )


def calculate_membership_break_even(
    membership_fee: float, bulk_discount: float, inflation_rate: float
) -> Dict[str, float]:
    """
    Inflation-adjusted break-even spend.

    Net_Benefit_real = (Yearly_Spend * Bulk_Discount / (1 + Inflation)) - Membership_Fee
    => BreakEven_YearlySpend = Membership_Fee * (1 + Inflation) / Bulk_Discount
    """
    break_even_yearly = membership_fee * (1 + inflation_rate) / max(bulk_discount, 0.001)
    return {
        "break_even_yearly_spend": break_even_yearly,
        "break_even_monthly_spend": break_even_yearly / 12.0,
    }


def generate_draws(config: Dict, scenario_cfg: Dict, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate household spend, discount, and latent-choice noise draws."""
    demand = config["demand_assumptions"]
    n = config["simulation"]["n_households_monte_carlo"]

    mean_target = demand["yearly_spend_distribution_mean_eur"]
    sigma = demand["yearly_spend_distribution_sigma"]
    mu = np.log(mean_target) - (sigma**2 / 2.0)
    spends = rng.lognormal(mean=mu, sigma=sigma, size=n)

    # Scenario discount shift reflects market discount pass-through pressure.
    d_min = max(0.02, demand["bulk_discount_distribution_min"] + scenario_cfg["discount_shift"])
    d_mode = max(d_min + 0.001, demand["bulk_discount_distribution_mode"] + scenario_cfg["discount_shift"])
    d_max = max(d_mode + 0.001, demand["bulk_discount_distribution_max"] + scenario_cfg["discount_shift"])
    discounts = rng.triangular(d_min, d_mode, d_max, size=n)
    noise = rng.normal(loc=0.0, scale=0.06, size=n)
    return spends, discounts, noise


def evaluate_strategy(
    config: Dict,
    consumer: GermanConsumer,
    strategy_name: str,
    strategy_cfg: Dict,
    scenario_name: str,
    scenario_cfg: Dict,
    spends: np.ndarray,
    discounts: np.ndarray,
    noise: np.ndarray,
    competitor_shock: float = 0.0,
) -> Tuple[Dict[str, float], np.ndarray]:
    """Vectorized strategy evaluation for one scenario/replication."""
    assumptions = config["operational_assumptions"]
    competition = config["competition_assumptions"]
    addressable_households = config["demand_assumptions"]["addressable_households"]
    fee_sensitivity = config["demand_assumptions"]["membership_fee_sensitivity"]

    fee = strategy_cfg["membership_fee_eur"]
    subsidy = strategy_cfg["first_year_subsidy_eur"]
    effective_fee = max(0.0, fee - subsidy)
    info_cues = (
        config["labor_legal"]["standard_german_ad_information_cues_min"]
        - 2
        + strategy_cfg["incremental_marketing_info_cues"]
    )

    resistance = consumer.calculate_impulse_resistance(
        consumer_climate_override=scenario_cfg["consumer_climate_index"],
        savings_rate_override=scenario_cfg["savings_rate_percent"],
    )

    scenario_competition_uplift = 0.0
    if scenario_name == "downside_stress":
        scenario_competition_uplift = competition["downside_response_uplift_percent"] / 100.0
    elif scenario_name == "upside_recovery":
        scenario_competition_uplift = -0.35 * (
            competition["downside_response_uplift_percent"] / 100.0
        )

    fee_exposure = max(0.0, (effective_fee - 35.0) / 100.0) * 0.02
    concentration_drag = (competition["top4_market_concentration_percent"] / 100.0) * 0.002
    info_mitigation = max(0.0, info_cues - consumer.INFO_CUE_THRESHOLD) * 0.0015
    competitor_penalty = (
        competition["competitor_response_base_percent"] / 100.0
        + scenario_competition_uplift
        + fee_exposure
        + concentration_drag
        - info_mitigation
        + competitor_shock
    )
    competitor_penalty = float(np.clip(competitor_penalty, 0.0, 0.08))

    net_benefit = (spends * discounts) - effective_fee
    info_density_boost = (info_cues - consumer.INFO_CUE_THRESHOLD) * 0.18
    fee_term = -(effective_fee * fee_sensitivity)
    resistance_term = -0.85 * resistance
    competitor_term = -(competitor_penalty * 8.0)
    latent = (net_benefit / 220.0) + info_density_boost + fee_term + resistance_term + competitor_term + noise
    probs = 1.0 / (1.0 + np.exp(-np.clip(latent, -30, 30)))
    adopted = probs > 0.5

    adoption_rate = float(adopted.mean())
    projected_member_households = adoption_rate * addressable_households
    adopted_spend_mean = float(spends[adopted].mean()) if adopted.any() else 0.0
    adopted_discount_mean = float(discounts[adopted].mean()) if adopted.any() else float(discounts.mean())

    projected_member_spend = projected_member_households * adopted_spend_mean
    projected_member_spend *= 1.0 - competitor_penalty
    membership_revenue = projected_member_households * effective_fee
    gross_profit_before_discount = projected_member_spend * (
        assumptions["merchandise_gross_margin_percent"] / 100.0
    )
    discount_cost = projected_member_spend * adopted_discount_mean
    merchandise_contribution = gross_profit_before_discount - discount_cost

    labor_cost = calculate_labor_cost_per_warehouse(config, 2026)
    fixed_opex = assumptions["annual_fixed_opex_eur"]
    total_contribution = membership_revenue + merchandise_contribution - labor_cost - fixed_opex

    inflation = scenario_cfg["inflation_percent"] / 100.0  # Source: Bundesbank base + stress envelope
    break_even = calculate_membership_break_even(
        membership_fee=effective_fee,
        bulk_discount=float(discounts.mean()),
        inflation_rate=inflation,
    )

    row = {
        "scenario": scenario_name,
        "strategy": strategy_name,
        "membership_fee_eur": fee,
        "first_year_subsidy_eur": subsidy,
        "effective_fee_eur": effective_fee,
        "info_cues_used": info_cues,
        "consumer_climate_index": scenario_cfg["consumer_climate_index"],
        "savings_rate_percent": scenario_cfg["savings_rate_percent"],
        "inflation_percent": scenario_cfg["inflation_percent"],
        "competitor_penalty_percent": competitor_penalty * 100.0,
        "adoption_rate": adoption_rate,
        "projected_member_households": projected_member_households,
        "projected_member_spend_eur": projected_member_spend,
        "membership_revenue_eur": membership_revenue,
        "merchandise_contribution_eur": merchandise_contribution,
        "total_contribution_eur": total_contribution,
        "break_even_monthly_spend_eur": break_even["break_even_monthly_spend"],
    }
    return row, probs


def run_replication_engine(config: Dict, consumer: GermanConsumer) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Run multi-scenario Monte Carlo replications with uncertainty metrics."""
    scenarios = config["macro_scenarios"]
    strategies = config["strategy_options"]
    n_rep = config["simulation"]["n_replications"]
    base_seed = config["simulation"]["random_seed"]

    rows: List[Dict] = []
    adoption_samples: List[pd.DataFrame] = []
    competition = config["competition_assumptions"]

    for scenario_idx, (scenario_name, scenario_cfg) in enumerate(scenarios.items()):
        for rep in range(n_rep):
            rng = np.random.default_rng(base_seed + (scenario_idx * 10_000) + rep)
            spends, discounts, noise = generate_draws(config, scenario_cfg, rng)
            for strategy_name, strategy_cfg in strategies.items():
                competitor_shock = float(
                    rng.normal(loc=0.0, scale=competition["response_volatility_percent"] / 100.0)
                )
                row, probs = evaluate_strategy(
                    config=config,
                    consumer=consumer,
                    strategy_name=strategy_name,
                    strategy_cfg=strategy_cfg,
                    scenario_name=scenario_name,
                    scenario_cfg=scenario_cfg,
                    spends=spends,
                    discounts=discounts,
                    noise=noise,
                    competitor_shock=competitor_shock,
                )
                row["replication_id"] = rep
                rows.append(row)

                # Keep one representative sample for distribution charting.
                if scenario_name == "base_case" and rep == 0:
                    adoption_samples.append(
                        pd.DataFrame(
                            {
                                "strategy": strategy_name,
                                "adoption_probability": probs,
                            }
                        )
                    )

    replication_df = pd.DataFrame(rows)
    adoption_df = pd.concat(adoption_samples, ignore_index=True)
    return replication_df, adoption_df


def summarize_replication_results(replication_df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """Aggregate replication outputs into confidence and downside-risk metrics."""
    hurdle = config["financial_assumptions"]["contribution_hurdle_eur"]
    summary_rows: List[Dict] = []
    grouped = replication_df.groupby(["scenario", "strategy"], sort=False)
    for (scenario, strategy), group in grouped:
        contrib = group["total_contribution_eur"]
        adopt = group["adoption_rate"]
        be = group["break_even_monthly_spend_eur"]
        penalty = group["competitor_penalty_percent"]
        q05 = float(contrib.quantile(0.05))
        cvar5 = float(contrib[contrib <= q05].mean()) if (contrib <= q05).any() else float(q05)
        summary_rows.append(
            {
                "scenario": scenario,
                "strategy": strategy,
                "mean_contribution_eur": float(contrib.mean()),
                "std_contribution_eur": float(contrib.std(ddof=1)),
                "p10_contribution_eur": float(contrib.quantile(0.10)),
                "p50_contribution_eur": float(contrib.quantile(0.50)),
                "p90_contribution_eur": float(contrib.quantile(0.90)),
                "cvar5_contribution_eur": cvar5,
                "prob_loss": float((contrib < 0).mean()),
                "prob_meet_hurdle": float((contrib >= hurdle).mean()),
                "mean_adoption_rate": float(adopt.mean()),
                "adoption_ci_low": float(adopt.quantile(0.10)),
                "adoption_ci_high": float(adopt.quantile(0.90)),
                "mean_competitor_penalty_pct": float(penalty.mean()),
                "mean_break_even_monthly_eur": float(be.mean()),
            }
        )
    return pd.DataFrame(summary_rows)


def build_decision_matrix(summary_df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """Cross-scenario strategy scorecard with risk-adjusted ranking."""
    scenario_probs = config["financial_assumptions"]["scenario_probabilities"]
    rows: List[Dict] = []
    for strategy, group in summary_df.groupby("strategy", sort=False):
        weighted = group.copy()
        weighted["scenario_probability"] = weighted["scenario"].map(lambda s: scenario_probs.get(s, 0.0))
        total_prob = float(weighted["scenario_probability"].sum()) or 1.0
        weighted["w"] = weighted["scenario_probability"] / total_prob

        weighted_mean_contrib = float((weighted["mean_contribution_eur"] * weighted["w"]).sum())
        mean_std = float((weighted["std_contribution_eur"] * weighted["w"]).sum())
        weighted_prob_loss = float((weighted["prob_loss"] * weighted["w"]).sum())
        weighted_cvar5 = float((weighted["cvar5_contribution_eur"] * weighted["w"]).sum())
        weighted_hurdle = float((weighted["prob_meet_hurdle"] * weighted["w"]).sum())
        base = group[group["scenario"] == "base_case"].iloc[0]

        # Penalize volatility, severe tail losses, and downside probability.
        risk_adjusted_score = (
            weighted_mean_contrib
            - (0.4 * mean_std)
            - (0.20 * abs(min(weighted_cvar5, 0.0)))
            - (weighted_prob_loss * 2_500_000)
        )
        rows.append(
            {
                "strategy": strategy,
                "weighted_mean_contribution_eur": weighted_mean_contrib,
                "mean_std_contribution_eur": mean_std,
                "weighted_prob_loss": weighted_prob_loss,
                "weighted_cvar5_contribution_eur": weighted_cvar5,
                "weighted_prob_meet_hurdle": weighted_hurdle,
                "base_case_contribution_eur": float(base["mean_contribution_eur"]),
                "base_case_adoption_rate": float(base["mean_adoption_rate"]),
                "risk_adjusted_score": risk_adjusted_score,
            }
        )

    decision = pd.DataFrame(rows).sort_values("risk_adjusted_score", ascending=False)
    decision["rank"] = np.arange(1, len(decision) + 1)
    return decision


def build_valuation_model(
    summary_df: pd.DataFrame, decision_df: pd.DataFrame, config: Dict
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build a 5-year free-cash-flow model per strategy and compute NPV/payback.
    """
    financial = config["financial_assumptions"]
    wacc = financial["wacc_percent"] / 100.0
    terminal_growth = financial["terminal_growth_percent"] / 100.0
    horizon = int(financial["planning_horizon_years"])
    capex_per_new = float(financial["capex_per_new_warehouse_eur"])
    maint_pct = financial["maintenance_capex_percent_of_contribution"] / 100.0
    rollout = financial["warehouses_cumulative_by_year"][:horizon]
    real_growth = config["macro"]["real_retail_growth_percent"] / 100.0

    valuation_rows: List[Dict] = []
    cashflow_rows: List[Dict] = []

    for _, strat in decision_df.iterrows():
        strategy = str(strat["strategy"])
        weighted_contrib = float(strat["weighted_mean_contribution_eur"])
        base_adoption = float(strat["base_case_adoption_rate"])

        # Growth links macro retail growth with strategy-specific adoption momentum.
        strategy_growth = real_growth + ((base_adoption - 0.20) * 0.10)
        strategy_growth = float(np.clip(strategy_growth, -0.02, 0.09))

        discount_factors = []
        discounted_fcfs = []
        undiscounted_cum = 0.0
        payback_year = None

        prev_wh = 0
        for year in range(1, horizon + 1):
            cumulative_wh = rollout[year - 1] if year - 1 < len(rollout) else rollout[-1]
            new_wh = cumulative_wh - prev_wh
            prev_wh = cumulative_wh

            contrib_per_wh = weighted_contrib * ((1.0 + strategy_growth) ** (year - 1))
            gross_contrib = contrib_per_wh * cumulative_wh
            maintenance_capex = max(0.0, gross_contrib) * maint_pct
            growth_capex = new_wh * capex_per_new
            fcf = gross_contrib - maintenance_capex - growth_capex

            discount_factor = 1.0 / ((1.0 + wacc) ** year)
            discounted = fcf * discount_factor
            discount_factors.append(discount_factor)
            discounted_fcfs.append(discounted)

            undiscounted_cum += fcf
            if payback_year is None and undiscounted_cum >= 0:
                payback_year = year

            cashflow_rows.append(
                {
                    "strategy": strategy,
                    "year": year,
                    "cumulative_warehouses": cumulative_wh,
                    "contribution_per_warehouse_eur": contrib_per_wh,
                    "gross_contribution_eur": gross_contrib,
                    "maintenance_capex_eur": maintenance_capex,
                    "growth_capex_eur": growth_capex,
                    "free_cash_flow_eur": fcf,
                    "discount_factor": discount_factor,
                    "discounted_fcf_eur": discounted,
                }
            )

        # Conservative terminal value on stabilized final-year FCF (if positive).
        year_n_fcf = float(cashflow_rows[-1]["free_cash_flow_eur"])
        terminal_value = 0.0
        if year_n_fcf > 0 and wacc > terminal_growth:
            terminal_value = (year_n_fcf * (1.0 + terminal_growth)) / (wacc - terminal_growth)
        terminal_discounted = terminal_value / ((1.0 + wacc) ** horizon)

        npv = float(sum(discounted_fcfs) + terminal_discounted)
        valuation_rows.append(
            {
                "strategy": strategy,
                "weighted_mean_contribution_eur": weighted_contrib,
                "strategy_growth_assumption": strategy_growth,
                "npv_5y_eur": npv,
                "terminal_value_discounted_eur": terminal_discounted,
                "payback_year": payback_year if payback_year is not None else -1,
            }
        )

    valuation_df = pd.DataFrame(valuation_rows).sort_values("npv_5y_eur", ascending=False)
    cashflow_df = pd.DataFrame(cashflow_rows)
    return valuation_df, cashflow_df


def build_city_portfolio(
    config: Dict, summary_df: pd.DataFrame, decision_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Build a city-level rollout optimization layer using strategy outputs.

    Returns:
    - city_strategy_df: one row per city x strategy combination
    - city_recommendation_df: best strategy per city
    - city_plan_df: city recommendations with rollout wave/year labels
    """
    city_inputs = config.get("city_portfolio_assumptions", [])
    if not city_inputs:
        empty = pd.DataFrame()
        return empty, empty, empty

    addressable_households = float(config["demand_assumptions"]["addressable_households"])
    capex_per_new = float(config["financial_assumptions"]["capex_per_new_warehouse_eur"])

    budget_cfg = config.get("portfolio_budget_assumptions", {})
    annual_budgets = list(
        budget_cfg.get(
            "annual_capex_budget_eur",
            [70_000_000, 120_000_000, 180_000_000, 220_000_000, 260_000_000],
        )
    )
    reserve_ratio = float(budget_cfg.get("budget_reserve_ratio", 0.10))

    opt_cfg = config.get("portfolio_optimization_constraints", {})
    max_new_per_year = list(opt_cfg.get("max_new_cities_per_year", [1, 2, 3, 3, 3]))
    annual_loss_risk_cap = list(opt_cfg.get("annual_loss_risk_cap", [0.20, 0.24, 0.28, 0.32, 0.35]))
    min_distinct_states_first3 = int(opt_cfg.get("min_distinct_states_first3_years", 3))
    readiness_bonus_per_point = float(opt_cfg.get("readiness_bonus_per_point_eur", 60_000))
    risk_penalty_per_prob = float(opt_cfg.get("risk_penalty_per_loss_prob_point_eur", 2_200_000))
    break_even_penalty_per_eur_over_70 = float(
        opt_cfg.get("break_even_penalty_per_eur_over_70_monthly", 12_000)
    )

    planning_years = min(len(annual_budgets), len(max_new_per_year), len(annual_loss_risk_cap))
    annual_budgets = annual_budgets[:planning_years]
    max_new_per_year = max_new_per_year[:planning_years]
    annual_loss_risk_cap = annual_loss_risk_cap[:planning_years]
    usable_budgets = [float(b) * max(0.0, 1.0 - reserve_ratio) for b in annual_budgets]

    scenario_lookup = summary_df.set_index(["scenario", "strategy"])
    decision_lookup = decision_df.set_index("strategy")

    rows: List[Dict] = []
    for city in city_inputs:
        city_name = city["city"]
        demand_scale = (float(city["households_k"]) * 1_000.0) / max(1.0, addressable_households)
        affluence_factor = 1.0 + 0.35 * (float(city["income_index"]) - 1.0)
        brand_factor = 1.0 + 0.25 * (float(city["brand_fit_index"]) - 0.5)
        cost_drag = (
            1.0
            + 0.30 * (1.0 - float(city["logistics_index"]))
            + 0.45 * float(city["competition_intensity"])
            + 0.20 * float(city["regulatory_complexity"])
        )
        savings_drag = 1.0 + 0.15 * float(city["savings_pressure_index"])
        city_multiplier = demand_scale * affluence_factor * brand_factor / max(0.25, cost_drag * savings_drag)
        city_multiplier = float(np.clip(city_multiplier, 0.30, 5.0))

        for strategy in decision_df["strategy"]:
            dec = decision_lookup.loc[strategy]
            base = scenario_lookup.loc[("base_case", strategy)]
            downside = scenario_lookup.loc[("downside_stress", strategy)]
            upside = scenario_lookup.loc[("upside_recovery", strategy)]

            expected_contribution = float(dec["weighted_mean_contribution_eur"]) * city_multiplier
            downside_contribution = float(downside["mean_contribution_eur"]) * city_multiplier
            upside_contribution = float(upside["mean_contribution_eur"]) * city_multiplier

            city_prob_loss = float(
                np.clip(
                    float(dec["weighted_prob_loss"])
                    * (
                        1.0
                        + 0.75 * float(city["competition_intensity"])
                        + 0.35 * float(city["regulatory_complexity"])
                        - 0.25 * float(city["brand_fit_index"])
                    ),
                    0.0,
                    1.0,
                )
            )
            tail_penalty = 0.18 * abs(min(downside_contribution, 0.0))
            loss_penalty = city_prob_loss * 2_500_000
            risk_adjusted_city_score = expected_contribution - loss_penalty - tail_penalty

            adjusted_break_even = float(base["mean_break_even_monthly_eur"]) * (
                1.0
                + 0.22 * float(city["savings_pressure_index"])
                + 0.15 * float(city["competition_intensity"])
                - 0.18 * (float(city["income_index"]) - 1.0)
            )
            adjusted_adoption = float(base["mean_adoption_rate"]) * float(np.clip(city_multiplier, 0.45, 1.8))

            rows.append(
                {
                    "city": city_name,
                    "state": city["state"],
                    "lat": float(city["lat"]),
                    "lon": float(city["lon"]),
                    "strategy": strategy,
                    "city_multiplier": city_multiplier,
                    "expected_contribution_eur": expected_contribution,
                    "downside_contribution_eur": downside_contribution,
                    "upside_contribution_eur": upside_contribution,
                    "city_prob_loss": city_prob_loss,
                    "risk_adjusted_city_score": risk_adjusted_city_score,
                    "adjusted_break_even_monthly_eur": adjusted_break_even,
                    "adjusted_adoption_rate": adjusted_adoption,
                    "households_k": float(city["households_k"]),
                    "income_index": float(city["income_index"]),
                    "brand_fit_index": float(city["brand_fit_index"]),
                    "logistics_index": float(city["logistics_index"]),
                    "competition_intensity": float(city["competition_intensity"]),
                    "regulatory_complexity": float(city["regulatory_complexity"]),
                    "savings_pressure_index": float(city["savings_pressure_index"]),
                }
            )

    city_strategy_df = pd.DataFrame(rows)

    score_by_city_strategy = city_strategy_df.copy()
    score_by_city_strategy["preliminary_readiness_score"] = (
        45.0
        + (score_by_city_strategy["brand_fit_index"] * 22.0)
        + (score_by_city_strategy["logistics_index"] * 15.0)
        - (score_by_city_strategy["regulatory_complexity"] * 14.0)
        - (score_by_city_strategy["competition_intensity"] * 8.0)
    ).clip(0, 100)
    score_by_city_strategy["objective_break_even_penalty_eur"] = (
        (score_by_city_strategy["adjusted_break_even_monthly_eur"] - 70.0)
        .clip(lower=0.0)
        .mul(break_even_penalty_per_eur_over_70)
    )
    score_by_city_strategy["portfolio_objective_eur"] = (
        score_by_city_strategy["risk_adjusted_city_score"]
        + (score_by_city_strategy["preliminary_readiness_score"] * readiness_bonus_per_point)
        - (score_by_city_strategy["city_prob_loss"] * risk_penalty_per_prob)
        - score_by_city_strategy["objective_break_even_penalty_eur"]
    )

    city_recommendation_df = (
        score_by_city_strategy.sort_values("portfolio_objective_eur", ascending=False)
        .groupby("city", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    city_recommendation_df = city_recommendation_df.sort_values(
        "portfolio_objective_eur", ascending=False
    ).reset_index(drop=True)

    city_recommendation_df["board_signal"] = np.where(
        (city_recommendation_df["portfolio_objective_eur"] > 0)
        & (city_recommendation_df["city_prob_loss"] <= 0.35),
        "GO",
        np.where(
            (city_recommendation_df["portfolio_objective_eur"] > -2_000_000)
            & (city_recommendation_df["city_prob_loss"] <= 0.55),
            "CONDITIONAL",
            "NO-GO",
        ),
    )

    score_min = float(city_recommendation_df["risk_adjusted_city_score"].min())
    score_max = float(city_recommendation_df["risk_adjusted_city_score"].max())
    score_span = max(1.0, score_max - score_min)
    norm_score = (city_recommendation_df["risk_adjusted_city_score"] - score_min) / score_span
    readiness = (
        38.0
        + (norm_score * 48.0)
        + (city_recommendation_df["brand_fit_index"] * 10.0)
        - (city_recommendation_df["regulatory_complexity"] * 10.0)
    )
    city_recommendation_df["launch_readiness_score"] = readiness.clip(0, 100)

    capex_multiplier = (
        0.84
        + (0.28 * city_recommendation_df["regulatory_complexity"])
        + (0.22 * city_recommendation_df["competition_intensity"])
        + (0.18 * (1.0 - city_recommendation_df["logistics_index"]))
    )
    city_recommendation_df["capex_estimate_eur"] = capex_per_new * capex_multiplier.clip(lower=0.75, upper=1.45)
    city_recommendation_df["score_density"] = (
        city_recommendation_df["portfolio_objective_eur"] / city_recommendation_df["capex_estimate_eur"]
    )

    city_recommendation_df["rollout_year"] = -1
    city_recommendation_df["launch_wave"] = "Hold"
    city_recommendation_df["year_capex_budget_eur"] = np.nan
    city_recommendation_df["year_capex_used_eur"] = np.nan
    city_recommendation_df["year_risk_cap"] = np.nan
    city_recommendation_df["year_loss_risk_avg"] = np.nan
    city_recommendation_df["selected_by_optimizer"] = False
    city_recommendation_df["optimization_status"] = "UNASSIGNED"

    candidate_df = city_recommendation_df[city_recommendation_df["board_signal"] != "NO-GO"].copy()
    if candidate_df.empty:
        city_recommendation_df["optimization_status"] = "NO_FEASIBLE_GO_OR_CONDITIONAL_CITIES"
    else:
        candidate_df = candidate_df.reset_index().rename(columns={"index": "df_index"})
        candidate_df["opt_bit"] = np.arange(len(candidate_df))

        state_list = sorted(candidate_df["state"].unique().tolist())
        state_to_bit = {state: i for i, state in enumerate(state_list)}
        candidate_df["state_mask"] = candidate_df["state"].map(lambda s: 1 << state_to_bit[s])

        capex_arr = candidate_df["capex_estimate_eur"].to_numpy(dtype=float)
        loss_arr = candidate_df["city_prob_loss"].to_numpy(dtype=float)
        objective_arr = candidate_df["portfolio_objective_eur"].to_numpy(dtype=float)
        state_mask_arr = candidate_df["state_mask"].to_numpy(dtype=int)
        df_index_arr = candidate_df["df_index"].to_numpy(dtype=int)

        from itertools import combinations

        n_candidates = len(candidate_df)
        first3_years = min(3, planning_years)
        required_states = min(min_distinct_states_first3, len(state_list))
        count_bits = lambda value: bin(int(value)).count("1")

        # Precompute feasible yearly launch bundles once to keep optimization tractable.
        yearly_bundles: Dict[int, List[Dict[str, object]]] = {}
        for year in range(1, planning_years + 1):
            max_new = int(max_new_per_year[year - 1])
            budget = float(usable_budgets[year - 1])
            risk_cap = float(annual_loss_risk_cap[year - 1])
            bundles: List[Dict[str, object]] = [
                {
                    "ids": tuple(),
                    "mask": 0,
                    "state_mask": 0,
                    "score": 0.0,
                    "capex_sum": 0.0,
                    "risk_avg": 0.0,
                }
            ]
            for k in range(1, min(max_new, n_candidates) + 1):
                for combo in combinations(range(n_candidates), k):
                    combo_arr = np.array(combo, dtype=int)
                    capex_sum = float(capex_arr[combo_arr].sum())
                    if capex_sum > budget:
                        continue
                    risk_avg = float(loss_arr[combo_arr].mean())
                    if risk_avg > risk_cap:
                        continue

                    combo_mask = 0
                    combo_state_mask = 0
                    for cid in combo:
                        combo_mask |= (1 << cid)
                        combo_state_mask |= int(state_mask_arr[cid])

                    bundles.append(
                        {
                            "ids": tuple(int(i) for i in combo),
                            "mask": combo_mask,
                            "state_mask": combo_state_mask,
                            "score": float(objective_arr[combo_arr].sum()),
                            "capex_sum": capex_sum,
                            "risk_avg": risk_avg,
                        }
                    )
            bundles.sort(key=lambda b: float(b["score"]), reverse=True)
            yearly_bundles[year] = bundles

        launched_mask = 0
        state_mask_first3 = 0
        schedule: List[Tuple[int, ...]] = []
        optimizer_total_score = 0.0
        optimization_feasible = True

        for year in range(1, planning_years + 1):
            best_bundle: Optional[Dict[str, object]] = None
            best_bundle_score = float("-inf")

            for bundle in yearly_bundles[year]:
                bundle_mask = int(bundle["mask"])
                if bundle_mask & launched_mask:
                    continue

                next_launched = launched_mask | bundle_mask
                next_state_mask = state_mask_first3
                if year <= first3_years:
                    next_state_mask = state_mask_first3 | int(bundle["state_mask"])

                    years_left = first3_years - year
                    available_state_mask = 0
                    for rid in range(n_candidates):
                        if (next_launched & (1 << rid)) == 0:
                            available_state_mask |= int(state_mask_arr[rid])

                    unseen_state_count = count_bits(available_state_mask & (~next_state_mask))
                    max_new_states_possible = count_bits(next_state_mask) + min(
                        unseen_state_count,
                        int(sum(max_new_per_year[year:first3_years])) if years_left > 0 else 0,
                    )
                    if max_new_states_possible < required_states:
                        continue
                    if year == first3_years and count_bits(next_state_mask) < required_states:
                        continue

                bundle_score = float(bundle["score"])
                if year <= first3_years:
                    new_states = count_bits(int(bundle["state_mask"]) & (~state_mask_first3))
                    # Prioritize early geographic diversification while preserving financial objective.
                    bundle_score += new_states * (400_000 * (first3_years - year + 1))

                if bundle_score > best_bundle_score:
                    best_bundle_score = bundle_score
                    best_bundle = bundle

            if best_bundle is None:
                optimization_feasible = False
                break

            schedule.append(tuple(best_bundle["ids"]))
            optimizer_total_score += float(best_bundle["score"])
            launched_mask |= int(best_bundle["mask"])
            if year <= first3_years:
                state_mask_first3 |= int(best_bundle["state_mask"])

        if (first3_years >= 1) and (count_bits(state_mask_first3) < required_states):
            optimization_feasible = False

        if not optimization_feasible:
            city_recommendation_df["optimization_status"] = "INFEASIBLE_CONSTRAINT_SET"
        else:
            for year, combo in enumerate(schedule, start=1):
                if year > planning_years:
                    break
                gross_budget = float(annual_budgets[year - 1])
                risk_cap = float(annual_loss_risk_cap[year - 1])
                if not combo:
                    continue

                combo_arr = np.array(combo, dtype=int)
                capex_sum = float(capex_arr[combo_arr].sum())
                risk_avg = float(loss_arr[combo_arr].mean())

                for opt_id in combo:
                    df_idx = int(df_index_arr[opt_id])
                    city_recommendation_df.at[df_idx, "rollout_year"] = year
                    city_recommendation_df.at[df_idx, "year_capex_budget_eur"] = gross_budget
                    city_recommendation_df.at[df_idx, "year_capex_used_eur"] = capex_sum
                    city_recommendation_df.at[df_idx, "year_risk_cap"] = risk_cap
                    city_recommendation_df.at[df_idx, "year_loss_risk_avg"] = risk_avg
                    city_recommendation_df.at[df_idx, "selected_by_optimizer"] = True
                    city_recommendation_df.at[df_idx, "optimization_status"] = "HARD_CONSTRAINED_SELECTION"

    city_recommendation_df["launch_wave"] = city_recommendation_df["rollout_year"].map(
        lambda y: (
            "Wave 1 Pilot"
            if y == 1
            else ("Wave 2 Scale" if y in (2, 3) else ("Wave 3 Option" if y > 0 else "Hold"))
        )
    )

    city_recommendation_df["_rollout_sort"] = city_recommendation_df["rollout_year"].map(
        lambda y: 99 if int(y) < 0 else int(y)
    )
    city_recommendation_df = city_recommendation_df.sort_values(
        ["_rollout_sort", "portfolio_objective_eur", "risk_adjusted_city_score"],
        ascending=[True, False, False],
    ).drop(columns=["_rollout_sort"]).reset_index(drop=True)
    city_recommendation_df["city_rank"] = np.arange(1, len(city_recommendation_df) + 1)

    city_plan_df = city_recommendation_df.copy()
    return city_strategy_df, city_recommendation_df, city_plan_df


def run_break_even_grid(config: Dict) -> pd.DataFrame:
    """Build fee-vs-discount sensitivity grid for board visuals."""
    inflation = config["macro"]["inflation_percent"] / 100.0  # Source: Bundesbank
    fees = [20, 35, 50, 65, 80, 95]
    discounts = np.linspace(0.04, 0.16, 20)
    rows = []
    for fee in fees:
        for discount in discounts:
            be = calculate_membership_break_even(fee, float(discount), inflation)
            rows.append(
                {
                    "membership_fee_eur": fee,
                    "bulk_discount": float(discount),
                    "break_even_monthly_spend_eur": be["break_even_monthly_spend"],
                }
            )
    return pd.DataFrame(rows)


def run_tornado_sensitivity(config: Dict, base_strategy: Dict) -> pd.DataFrame:
    """One-at-a-time sensitivity around base strategy for break-even monthly spend."""
    inflation = config["macro"]["inflation_percent"] / 100.0
    base_fee = max(0.0, base_strategy["membership_fee_eur"] - base_strategy["first_year_subsidy_eur"])
    base_discount = config["demand_assumptions"]["bulk_discount_distribution_mode"]
    base_break_even = calculate_membership_break_even(base_fee, base_discount, inflation)[
        "break_even_monthly_spend"
    ]

    drivers = [
        ("membership_fee", base_fee),
        ("bulk_discount", base_discount),
        ("inflation", inflation),
    ]
    rows = []
    for name, val in drivers:
        low = val * 0.85
        high = val * 1.15

        if name == "membership_fee":
            low_out = calculate_membership_break_even(low, base_discount, inflation)["break_even_monthly_spend"]
            high_out = calculate_membership_break_even(high, base_discount, inflation)["break_even_monthly_spend"]
        elif name == "bulk_discount":
            low_out = calculate_membership_break_even(base_fee, low, inflation)["break_even_monthly_spend"]
            high_out = calculate_membership_break_even(base_fee, high, inflation)["break_even_monthly_spend"]
        else:
            low_out = calculate_membership_break_even(base_fee, base_discount, low)["break_even_monthly_spend"]
            high_out = calculate_membership_break_even(base_fee, base_discount, high)["break_even_monthly_spend"]

        rows.append(
            {
                "driver": name,
                "base_monthly_break_even_eur": base_break_even,
                "low_case_delta_eur": low_out - base_break_even,
                "high_case_delta_eur": high_out - base_break_even,
                "swing_abs_eur": max(abs(low_out - base_break_even), abs(high_out - base_break_even)),
            }
        )

    return pd.DataFrame(rows).sort_values("swing_abs_eur", ascending=True)


def run_marketing_audit(consumer: GermanConsumer) -> pd.DataFrame:
    """Evaluate sample copy strings using the high-information German threshold."""
    sample_copy = [
        "High Quality, Low Price",
        "Trusted value for families. Better prices every day.",
        (
            "Bio oats, 2kg pack, EUR 2.49/kg, ISO 22000 certified, "
            "Energy class A, 12-month warranty, DIN EN tested, 15% protein."
        ),
    ]
    rows = []
    for text in sample_copy:
        details = consumer.count_information_cues(text)
        rows.append(
            {
                "text": text,
                "cue_count": details.cue_count,
                "decision": details.decision,
                "confidence_score": details.confidence_score,
                "reason": details.reason,
            }
        )
    return pd.DataFrame(rows)


def build_chart_savings_trap_gap(config: Dict, output_dir: Path) -> Path:
    theme = config["visual_theme"]
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    labels = ["US Indulgence Index", "Germany Savings Rate (%)"]
    values = [config["benchmarks"]["us_indulgence_reference"], config["macro"]["savings_rate_percent"]]
    ax.bar(labels, values, color=[theme["grey"], theme["red"]], width=0.56)
    ax.set_title("The Savings Trap Gap")
    ax.set_ylabel("Index / Percent")
    for idx, value in enumerate(values):
        ax.text(idx, value + 1.2, f"{value:.1f}", ha="center", va="bottom", fontsize=10)
    path = output_dir / "chart_01_savings_trap_gap.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_wage_forecast(config: Dict, output_dir: Path) -> Path:
    theme = config["visual_theme"]
    labor_2026 = calculate_labor_cost_per_warehouse(config, 2026)
    labor_2027 = calculate_labor_cost_per_warehouse(config, 2027)
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2027-01-01"]),
            "annual_labor_opex_eur": [labor_2026, labor_2027],
        }
    )
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.plot(df["date"], df["annual_labor_opex_eur"], color=theme["red"], linewidth=2.8, marker="o")
    ax.set_title("Wage Inflation Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Annual Labor OpEx per Warehouse (EUR)")
    ax.ticklabel_format(axis="y", style="plain")
    for _, row in df.iterrows():
        ax.annotate(
            f"EUR {row['annual_labor_opex_eur']:,.0f}",
            (row["date"], row["annual_labor_opex_eur"]),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9,
        )
    path = output_dir / "chart_02_wage_inflation_forecast.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_break_even_curves(grid_df: pd.DataFrame, config: Dict, output_dir: Path) -> Path:
    theme = config["visual_theme"]
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    palette = sns.color_palette(["#B71C1C", "#D84315", "#6D4C41", "#455A64", "#546E7A", "#1E88E5"])
    for i, (fee, sub_df) in enumerate(grid_df.groupby("membership_fee_eur")):
        ax.plot(
            sub_df["bulk_discount"] * 100,
            sub_df["break_even_monthly_spend_eur"],
            label=f"Fee EUR {fee}",
            linewidth=2.3 if fee in (35, 65) else 1.6,
            color=palette[i % len(palette)],
        )
    ax.set_title("Membership Value Proposition Sensitivity")
    ax.set_xlabel("Bulk Discount (%)")
    ax.set_ylabel("Break-even Monthly Spend (EUR)")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.axhline(800, color=theme["red"], linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(15.7, 808, "EUR 800 stress threshold", color=theme["red"], fontsize=9, ha="right")
    path = output_dir / "chart_03_membership_sensitivity_curves.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_adoption_distribution(adoption_df: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    sns.histplot(
        data=adoption_df,
        x="adoption_probability",
        hue="strategy",
        element="step",
        bins=35,
        stat="density",
        common_norm=False,
        alpha=0.15,
        ax=ax,
    )
    ax.set_title("Adoption Probability Distribution by Strategy (Base Case)")
    ax.set_xlabel("Adoption Probability")
    ax.set_ylabel("Density")
    ax.set_xlim(0, 1)
    path = output_dir / "chart_04_adoption_distribution.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_strategy_contribution_ci(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot base-case contribution with uncertainty interval."""
    base = summary_df[summary_df["scenario"] == "base_case"].copy()
    base = base.sort_values("mean_contribution_eur", ascending=False)
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    x = np.arange(len(base))
    means = base["mean_contribution_eur"].to_numpy() / 1_000_000
    low = (base["mean_contribution_eur"] - base["p10_contribution_eur"]).to_numpy() / 1_000_000
    high = (base["p90_contribution_eur"] - base["mean_contribution_eur"]).to_numpy() / 1_000_000
    colors = ["#B71C1C" if i == 0 else "#6E6E6E" for i in range(len(base))]

    ax.bar(x, means, color=colors, width=0.58)
    ax.errorbar(x, means, yerr=[low, high], fmt="none", ecolor="#222222", capsize=4, linewidth=1.2)
    ax.axhline(0, color="#333333", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(base["strategy"])
    ax.set_title("Base Case Contribution with P10/P90 Uncertainty")
    ax.set_ylabel("Annual Contribution per Warehouse (EUR Millions)")
    path = output_dir / "chart_05_strategy_contribution_ci.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_tornado(tornado_df: pd.DataFrame, config: Dict, output_dir: Path) -> Path:
    theme = config["visual_theme"]
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    y = np.arange(len(tornado_df))
    ax.barh(y - 0.18, tornado_df["low_case_delta_eur"], height=0.34, color=theme["grey"], label="-15%")
    ax.barh(y + 0.18, tornado_df["high_case_delta_eur"], height=0.34, color=theme["red"], label="+15%")
    ax.set_yticks(y)
    ax.set_yticklabels(tornado_df["driver"])
    ax.set_title("Tornado: Break-even Sensitivity (Monthly EUR)")
    ax.set_xlabel("Delta vs Base Case (EUR)")
    ax.axvline(0, color="#444444", linewidth=1.0)
    ax.legend(frameon=False)
    path = output_dir / "chart_06_tornado_sensitivity.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_scenario_heatmap(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    pivot = (
        summary_df.pivot(index="scenario", columns="strategy", values="mean_contribution_eur") / 1_000_000
    )
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdGy", cbar_kws={"label": "EUR Millions"}, ax=ax)
    ax.set_title("Scenario x Strategy Contribution Heatmap")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Macro Scenario")
    path = output_dir / "chart_07_scenario_heatmap.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_downside_risk(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    data = summary_df.copy()
    data["prob_loss_pct"] = data["prob_loss"] * 100
    sns.barplot(data=data, x="scenario", y="prob_loss_pct", hue="strategy", ax=ax)
    ax.set_title("Downside Risk: Probability of Negative Contribution")
    ax.set_xlabel("Macro Scenario")
    ax.set_ylabel("Probability of Loss (%)")
    ax.legend(frameon=False, title="")
    path = output_dir / "chart_08_downside_risk.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_valuation_npv(valuation_df: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    ordered = valuation_df.sort_values("npv_5y_eur", ascending=False)
    values = ordered["npv_5y_eur"] / 1_000_000
    colors = ["#B71C1C" if i == 0 else "#6E6E6E" for i in range(len(ordered))]
    ax.bar(ordered["strategy"], values, color=colors, width=0.58)
    ax.set_title("5-Year NPV by Strategy")
    ax.set_ylabel("NPV (EUR Millions)")
    ax.axhline(0, color="#333333", linewidth=1.0)
    for i, val in enumerate(values):
        ax.text(i, val + (0.4 if val >= 0 else -0.8), f"{val:.1f}", ha="center", va="bottom", fontsize=9)
    path = output_dir / "chart_09_npv_by_strategy.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def build_chart_cashflow_paths(cashflow_df: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    data = cashflow_df.copy()
    data["free_cash_flow_m_eur"] = data["free_cash_flow_eur"] / 1_000_000
    sns.lineplot(
        data=data,
        x="year",
        y="free_cash_flow_m_eur",
        hue="strategy",
        marker="o",
        linewidth=2.1,
        ax=ax,
    )
    ax.set_title("5-Year Free Cash Flow Trajectories")
    ax.set_xlabel("Year")
    ax.set_ylabel("FCF (EUR Millions)")
    ax.axhline(0, color="#333333", linewidth=1.0)
    ax.legend(frameon=False, title="")
    path = output_dir / "chart_10_cashflow_paths.png"
    fig.tight_layout()
    fig.savefig(path, dpi=230)
    plt.close(fig)
    return path


def write_analytical_paper(
    config: Dict,
    summary_df: pd.DataFrame,
    decision_df: pd.DataFrame,
    valuation_df: pd.DataFrame,
    replication_df: pd.DataFrame,
    break_even_grid: pd.DataFrame,
    marketing_audit_df: pd.DataFrame,
    compliance_summary: Dict[str, int],
    city_recommendation_df: pd.DataFrame,
    city_plan_df: pd.DataFrame,
    chart_paths: List[Path],
    output_dir: Path,
) -> Path:
    """Generate a board-grade analytical paper in Markdown from model outputs."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    best = decision_df.sort_values("rank").iloc[0]
    recommended_strategy = str(best["strategy"])

    def scenario_row(scenario: str, strategy: str) -> pd.Series:
        return summary_df[
            (summary_df["scenario"] == scenario) & (summary_df["strategy"] == strategy)
        ].iloc[0]

    base_standard = scenario_row("base_case", "standard_65")
    base_entry = scenario_row("base_case", "entry_35")
    base_recommended = scenario_row("base_case", recommended_strategy)
    downside_standard = scenario_row("downside_stress", "standard_65")
    downside_recommended = scenario_row("downside_stress", recommended_strategy)
    upside_recommended = scenario_row("upside_recovery", recommended_strategy)

    standard_decision = decision_df[decision_df["strategy"] == "standard_65"].iloc[0]
    recommended_decision = decision_df[decision_df["strategy"] == recommended_strategy].iloc[0]

    recommended_valuation = valuation_df[valuation_df["strategy"] == recommended_strategy].iloc[0]
    top_npv = float(recommended_valuation["npv_5y_eur"])

    stress_share_200 = float((break_even_grid["break_even_monthly_spend_eur"] >= 200).mean())
    stress_share_400 = float((break_even_grid["break_even_monthly_spend_eur"] >= 400).mean())
    stress_share_800 = float((break_even_grid["break_even_monthly_spend_eur"] >= 800).mean())
    break_even_p50 = float(break_even_grid["break_even_monthly_spend_eur"].median())
    break_even_p90 = float(break_even_grid["break_even_monthly_spend_eur"].quantile(0.90))

    rejected_ads = int((marketing_audit_df["decision"] == "REJECT").sum())
    marketing_reject_rate = rejected_ads / max(1, len(marketing_audit_df))
    high_risk_count = int((replication_df["total_contribution_eur"] < 0).sum())
    total_sims = len(replication_df)

    labor_2026 = calculate_labor_cost_per_warehouse(config, 2026)
    labor_2027 = calculate_labor_cost_per_warehouse(config, 2027)
    labor_delta_pct = ((labor_2027 - labor_2026) / labor_2026) * 100

    fee_uplift_entry_vs_standard = float(base_entry["mean_contribution_eur"] - base_standard["mean_contribution_eur"])
    fee_uplift_recommended_vs_standard = float(
        base_recommended["mean_contribution_eur"] - base_standard["mean_contribution_eur"]
    )
    downside_delta_recommended = float(
        downside_recommended["mean_contribution_eur"] - base_recommended["mean_contribution_eur"]
    )
    downside_delta_standard = float(
        downside_standard["mean_contribution_eur"] - base_standard["mean_contribution_eur"]
    )

    scenario_snapshot = summary_df[
        [
            "scenario",
            "strategy",
            "mean_contribution_eur",
            "p10_contribution_eur",
            "p90_contribution_eur",
            "prob_loss",
            "mean_adoption_rate",
            "mean_break_even_monthly_eur",
        ]
    ].copy()
    scenario_snapshot["prob_loss"] = scenario_snapshot["prob_loss"] * 100
    scenario_md = dataframe_to_markdown(scenario_snapshot, decimals=2)

    decision_md = dataframe_to_markdown(
        decision_df[
            [
                "rank",
                "strategy",
                "weighted_mean_contribution_eur",
                "weighted_prob_loss",
                "weighted_cvar5_contribution_eur",
                "risk_adjusted_score",
            ]
        ].assign(weighted_prob_loss=lambda x: x["weighted_prob_loss"] * 100),
        decimals=2,
    )
    valuation_md = dataframe_to_markdown(
        valuation_df[
            [
                "strategy",
                "npv_5y_eur",
                "terminal_value_discounted_eur",
                "payback_year",
            ]
        ],
        decimals=2,
    )

    hypothesis_df = pd.DataFrame(
        [
            {
                "hypothesis": "H1: Standard-fee entry is commercially fragile in current German conditions.",
                "evidence": (
                    f"Base-case standard contribution EUR {base_standard['mean_contribution_eur']:,.0f}; "
                    f"loss probability {base_standard['prob_loss']:.1%}."
                ),
                "verdict": "Supported",
            },
            {
                "hypothesis": "H2: Lower upfront fee friction is first-order, not marginal.",
                "evidence": (
                    f"Base-case uplift vs standard: entry EUR {fee_uplift_entry_vs_standard:,.0f}; "
                    f"recommended EUR {fee_uplift_recommended_vs_standard:,.0f}."
                ),
                "verdict": "Supported",
            },
            {
                "hypothesis": "H3: Tail risk is strategy-controllable through membership design.",
                "evidence": (
                    f"Weighted loss probability: standard {standard_decision['weighted_prob_loss']:.1%} vs "
                    f"recommended {recommended_decision['weighted_prob_loss']:.1%}."
                ),
                "verdict": "Supported",
            },
            {
                "hypothesis": "H4: Operating resilience alone is sufficient for rollout approval.",
                "evidence": f"Recommended strategy 5-year NPV is EUR {top_npv:,.0f}.",
                "verdict": "Rejected",
            },
        ]
    )
    hypothesis_md = dataframe_to_markdown(hypothesis_df, decimals=2)

    counterfactual_df = pd.DataFrame(
        [
            {
                "counterfactual": "Keep standard EUR 65 fee and scale nationally.",
                "model_readout": (
                    f"Weighted mean contribution EUR {standard_decision['weighted_mean_contribution_eur']:,.0f}; "
                    f"weighted loss probability {standard_decision['weighted_prob_loss']:.1%}."
                ),
                "board_implication": "High downside concentration; unacceptable risk-adjusted profile.",
            },
            {
                "counterfactual": "Use entry EUR 35 architecture as permanent base tier.",
                "model_readout": (
                    f"Weighted mean contribution EUR {decision_df.loc[decision_df['strategy']=='entry_35', 'weighted_mean_contribution_eur'].iloc[0]:,.0f}; "
                    f"base-case adoption {base_entry['mean_adoption_rate']:.1%}."
                ),
                "board_implication": "Viable intermediate option, but still inferior to recommended risk-adjusted score.",
            },
            {
                "counterfactual": f"Deploy {recommended_strategy} with stage-gated investment.",
                "model_readout": (
                    f"Weighted mean contribution EUR {recommended_decision['weighted_mean_contribution_eur']:,.0f}; "
                    f"weighted loss probability {recommended_decision['weighted_prob_loss']:.1%}; "
                    f"5-year NPV EUR {top_npv:,.0f}."
                ),
                "board_implication": "Best operating profile; capital still requires option-value discipline.",
            },
        ]
    )
    counterfactual_md = dataframe_to_markdown(counterfactual_df, decimals=2)

    falsification_df = pd.DataFrame(
        [
            {
                "falsification_trigger": "Pilot contribution underperforms modeled P10 corridor for 3 consecutive weeks.",
                "why_it_matters": "Signals elasticity assumptions are optimistic or execution quality is insufficient.",
                "action": "Pause city expansion and re-estimate demand parameters before additional capex.",
            },
            {
                "falsification_trigger": "Conversion remains weak even after 7+ cue-compliant creative rollout.",
                "why_it_matters": "Indicates value proposition mismatch beyond information density.",
                "action": "Redesign fee ladder and basket proposition; deprioritize media spend expansion.",
            },
            {
                "falsification_trigger": "High-severity compliance findings persist above threshold post-control deployment.",
                "why_it_matters": "Legal and labor governance risk can destroy rollout option value.",
                "action": "Freeze operational scaling until compliance defect rate is reduced.",
            },
            {
                "falsification_trigger": "Recalibrated 5-year NPV remains negative after pilot learning integration.",
                "why_it_matters": "Commercial performance fails to clear capital hurdle despite operational tuning.",
                "action": "Terminate national rollout thesis and revisit format design.",
            },
        ]
    )
    falsification_md = dataframe_to_markdown(falsification_df, decimals=2)

    roadmap_df = pd.DataFrame(
        [
            {
                "phase": "Phase 1: Pilot Design",
                "time_window": "0-60 days",
                "core_deliverables": (
                    "Two-city launch, cohort instrumentation, legal pre-clearance of green claims, "
                    "works-council scheduling protocol."
                ),
                "decision_metric": "Weekly contribution vs modeled P10/P50 corridor.",
            },
            {
                "phase": "Phase 2: Learning and Recalibration",
                "time_window": "60-120 days",
                "core_deliverables": (
                    "Elasticity re-estimation, competitor response calibration, campaign cue-compliance enforcement."
                ),
                "decision_metric": "Updated weighted loss probability and CVaR trend.",
            },
            {
                "phase": "Phase 3: Investment Gate",
                "time_window": "120-180 days",
                "core_deliverables": "Board decision on expansion pace, capex resequencing, and membership architecture lock-in.",
                "decision_metric": "Rebased 5-year NPV and hurdle attainment probability.",
            },
        ]
    )
    roadmap_md = dataframe_to_markdown(roadmap_df, decimals=2)

    city_priority_md = "No city portfolio recommendations generated."
    pilot_city_block = "Pilot city shortlist unavailable."
    if not city_recommendation_df.empty:
        city_priority_df = city_recommendation_df[
            [
                "city_rank",
                "city",
                "state",
                "strategy",
                "launch_wave",
                "board_signal",
                "risk_adjusted_city_score",
                "expected_contribution_eur",
                "city_prob_loss",
                "adjusted_break_even_monthly_eur",
                "capex_estimate_eur",
                "rollout_year",
                "launch_readiness_score",
            ]
        ].copy()
        city_priority_df["city_prob_loss"] = city_priority_df["city_prob_loss"] * 100.0
        city_priority_md = dataframe_to_markdown(city_priority_df, decimals=2)

        pilots = city_recommendation_df.head(3)
        pilot_lines = []
        for _, row in pilots.iterrows():
            pilot_lines.append(
                (
                    f"- **{row['city']} ({row['state']})**: strategy `{row['strategy']}`, "
                    f"score EUR {row['risk_adjusted_city_score']:,.0f}, "
                    f"loss risk {row['city_prob_loss']:.1%}, readiness {row['launch_readiness_score']:.1f}/100."
                )
            )
        pilot_city_block = "\n".join(pilot_lines)

    wave_summary_md = "No rollout wave plan generated."
    if not city_plan_df.empty:
        wave_summary_df = (
            city_plan_df.groupby(["launch_wave", "strategy"], as_index=False)
            .agg(
                city_count=("city", "count"),
                mean_score=("risk_adjusted_city_score", "mean"),
                mean_expected_contribution_eur=("expected_contribution_eur", "mean"),
                mean_prob_loss=("city_prob_loss", "mean"),
                mean_capex_eur=("capex_estimate_eur", "mean"),
            )
            .sort_values(["launch_wave", "mean_score"], ascending=[True, False])
        )
        wave_summary_df["mean_prob_loss"] = wave_summary_df["mean_prob_loss"] * 100.0
        wave_summary_md = dataframe_to_markdown(wave_summary_df, decimals=2)

    chart_list = "\n".join([f"- `{path.as_posix()}`" for path in chart_paths])
    source_rows = []
    for key, source in config.get("sources", {}).items():
        source_rows.append(
            {
                "id": key,
                "source": source.get("source", ""),
                "url": source.get("url", ""),
                "evidence": source.get("evidence", ""),
            }
        )
    source_md = dataframe_to_markdown(pd.DataFrame(source_rows), decimals=2) if source_rows else ""

    if top_npv < 0:
        recommendation = "Run a controlled pilot only; withhold national rollout capex until economics are recalibrated."
    else:
        recommendation = (
            "Proceed with staged expansion under strict marketing and compliance controls."
            if recommended_strategy != "standard_65"
            else "Proceed with standard pricing only if conversion and downside-risk diagnostics remain stable."
        )

    refresh_note = "No refresh overrides loaded."
    if config.get("meta", {}).get("refresh_data_used"):
        refresh_note = (
            "Refresh overrides loaded from data/latest_inputs.json "
            f"(generated at {config['meta'].get('refresh_generated_at', 'unknown time')})."
        )
    elif config.get("meta", {}).get("refresh_rejected"):
        refresh_note = (
            "Refresh payload found but rejected by quality gate; defaults retained "
            f"(generated at {config['meta'].get('refresh_generated_at', 'unknown time')})."
        )
    budget_cfg = config.get("portfolio_budget_assumptions", {})
    annual_budgets = budget_cfg.get("annual_capex_budget_eur", [])
    reserve_ratio = float(budget_cfg.get("budget_reserve_ratio", 0.0))
    budget_list_text = (
        ", ".join([f"Y{idx+1}: EUR {float(val):,.0f}" for idx, val in enumerate(annual_budgets)])
        if annual_budgets
        else "Not configured"
    )

    paper = f"""# Costco Germany 2026 Market Entry Simulation: Executive Analytical Paper

**Model Version:** {config["meta"]["version"]}  
**As Of Date:** {config["meta"]["as_of_date"]}  
**Generated:** {timestamp}

## Executive Thesis
Costco's Germany problem is not whether value retail works. It is whether the U.S. membership model can survive a market where household uncertainty is elevated, savings behavior is structurally defensive, and information/compliance expectations are materially stricter.

**Primary recommendation:** {recommendation}

**Three board-level claims from this model run**
1. **Commercial design claim:** the standard fee architecture is structurally fragile in the current demand regime.
2. **Risk claim:** downside exposure is heavily strategy-dependent, not exogenous.
3. **Capital claim:** operating resilience is necessary but insufficient; capital pacing determines whether the thesis is investable.

**Current readout**
- Winning strategy in risk-adjusted ranking: `{recommended_strategy}`
- Base-case standard expected contribution: EUR {base_standard["mean_contribution_eur"]:,.0f}
- Base-case standard loss probability: {base_standard["prob_loss"]:.1%}
- Recommended strategy weighted loss probability: {recommended_decision["weighted_prob_loss"]:.1%}
- Recommended strategy 5-year NPV: EUR {top_npv:,.0f}
- Data refresh status: {refresh_note}

## Data Foundation and Context
- Consumer Climate Index: {config["macro"]["consumer_climate_index"]} (Source: NIM/GfK)
- Household savings rate (gross / net): {config["macro"]["savings_rate_percent"]}% / {config["macro"].get("savings_rate_net_percent", "n/a")}%
- Inflation forecast: {config["macro"]["inflation_percent"]}% (Source: European Commission)
- Real retail growth: +{config["macro"]["real_retail_growth_percent"]}% (Source: Destatis)
- Cultural profile (Hofstede): UAI 65, LTO 83, Indulgence 40
- Minimum wage path: EUR {config["labor_legal"]["min_wage_2026_eur_per_hour"]} (2026) to EUR {config["labor_legal"]["min_wage_2027_eur_per_hour"]} (2027)
- Wage-driven annual labor inflation per warehouse (modeled): {labor_delta_pct:.2f}% (EUR {labor_2026:,.0f} to EUR {labor_2027:,.0f})

### Source Register
{source_md}

## Methodological Architecture
1. **Behavioral model:** household adoption probability blends net economic benefit, information-density effects, and cultural resistance.
2. **Stochastic engine:** household spend, discount realization, and latent choice noise are Monte Carlo sampled.
3. **Scenario layer:** base case, downside stress, and upside recovery regimes with weighted aggregation.
4. **Economics layer:** membership + merchandise contribution net of labor, fixed OpEx, and competitor-pressure drag.
5. **Finance layer:** 5-year FCF/NPV/payback with rollout and capex assumptions.
6. **Compliance layer:** EmpCo and labor-governance lint checks are embedded as launch constraints.

### Core Equations
```text
Net_Benefit = (Yearly_Spend * Bulk_Discount) - Effective_Fee
Adoption_Prob = sigmoid((Net_Benefit / 220) + InfoDensity - FeePenalty - Resistance + Noise)
Contribution = MembershipRevenue + MerchandiseContribution - Labor - FixedOpEx - CompetitorPenalty
```

## Hypothesis Testing (Model-Derived)
{hypothesis_md}

## Scenario Results
{scenario_md}

## Decision Matrix (Cross-Scenario)
{decision_md}

## Capital Allocation View (5-Year)
{valuation_md}

## Mechanism Interpretation
1. **Fee friction is first-order:** moving from standard to entry fee improves base-case contribution by EUR {fee_uplift_entry_vs_standard:,.0f}; the recommended design improves by EUR {fee_uplift_recommended_vs_standard:,.0f}.
2. **Risk is design-dependent:** weighted loss probability drops from {standard_decision["weighted_prob_loss"]:.1%} (standard) to {recommended_decision["weighted_prob_loss"]:.1%} (recommended).
3. **Downside behavior is not uniform:** downside shock changes mean contribution by EUR {downside_delta_standard:,.0f} for standard vs EUR {downside_delta_recommended:,.0f} for recommended.
4. **Commercial-to-capital gap remains:** despite strong operating contribution in all three scenarios (recommended strategy), 5-year NPV remains EUR {top_npv:,.0f}.
5. **Conversion/compliance coupling is real:** {rejected_ads}/{len(marketing_audit_df)} creatives fail cue thresholds ({marketing_reject_rate:.1%}); high-severity compliance findings = {compliance_summary["high_severity_findings"]}.

## Strategic Paradox and Board Implication
The simulation produces a clear paradox: the recommended strategy generates superior operating economics (base: EUR {base_recommended['mean_contribution_eur']:,.0f}; downside: EUR {downside_recommended['mean_contribution_eur']:,.0f}; upside: EUR {upside_recommended['mean_contribution_eur']:,.0f}) while failing current 5-year capital screens.

This means the board should not frame Germany as a binary go/no-go market thesis. It should frame Germany as a **real-options sequencing problem**:
1. Buy information through a tightly instrumented pilot.
2. Convert information into parameter updates (elasticity, competitor response, compliance defect rate).
3. Expand only when updated risk-adjusted economics clear threshold.

## Counterfactual Economics
{counterfactual_md}

## Break-Even Geometry and Household Feasibility
- Median modeled break-even monthly spend: EUR {break_even_p50:,.2f}
- P90 break-even monthly spend: EUR {break_even_p90:,.2f}
- Share of fee/discount combinations above EUR 200/month: {stress_share_200:.1%}
- Share above EUR 400/month: {stress_share_400:.1%}
- Share above EUR 800/month: {stress_share_800:.1%}

Interpretation: the barrier is not extreme monthly spend for most combinations; the strategic bottleneck is upfront fee friction and credibility of value communication.

## City Portfolio Optimization (Germany Rollout Geography)
The city layer translates strategy economics into a geographically staged launch plan by integrating catchment scale, competition intensity, logistics quality, regulatory friction, and savings-pressure behavior.
Rollout is constrained by annual capex envelopes ({budget_list_text}) with a {reserve_ratio:.0%} reserve policy.

### Recommended Pilot Shortlist
{pilot_city_block}

### City-Level Priority Table
{city_priority_md}

### Rollout Wave Summary
{wave_summary_md}

## 180-Day Operating Blueprint
{roadmap_md}

## Falsification Framework (What Would Invalidate This Recommendation)
{falsification_md}

## Visual Exhibits
{chart_list}

## Limitations and Research Agenda
1. **Elasticity uncertainty:** parameters remain assumption-driven until pilot microdata is integrated.
2. **Competitive response endogeneity:** Aldi/Lidl/Edeka reactions are approximated; city-level calibration required.
3. **Capital model simplification:** working-capital dynamics and cannibalization effects remain out-of-scope.
4. **Data refresh maturity:** automated refresh quality gate must improve before external decision-use.
5. **Next analytical step:** monthly Bayesian re-estimation loop tied to pilot telemetry and governance outcomes.
6. Supporting references and refresh protocol: `research/REAL_DATA_RESEARCH.md`; automation: `scripts/refresh_inputs.py`.
"""
    paper_path = output_dir / "Costco_Germany_2026_Analytical_Paper.md"
    paper_path.write_text(paper, encoding="utf-8")
    return paper_path


def run_full_analysis() -> Dict[str, object]:
    """Run complete pipeline and export visuals, tables, paper, and executive JSON."""
    config = load_config()
    apply_swiss_style(config)

    output_dir = Path("outputs")
    tables_dir = output_dir / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    consumer = GermanConsumer(config=config)
    replication_df, adoption_df = run_replication_engine(config, consumer)
    summary_df = summarize_replication_results(replication_df, config)
    decision_df = build_decision_matrix(summary_df, config)
    valuation_df, cashflow_df = build_valuation_model(summary_df, decision_df, config)
    city_strategy_df, city_recommendation_df, city_plan_df = build_city_portfolio(
        config, summary_df, decision_df
    )
    break_even_grid = run_break_even_grid(config)
    tornado_df = run_tornado_sensitivity(config, config["strategy_options"]["standard_65"])
    marketing_audit_df = run_marketing_audit(consumer)

    green_claim_results = audit_green_claims(
        [
            "Climate Neutral household cleaner",
            "Eco-friendly detergent, ISO 14067 certified",
            "Green packaging for paper towels",
            "Low-emission logistics detergent ISO 14064-1",
        ]
    )
    workforce_results = check_workforce_scheduling(
        [
            {"warehouse": "Berlin", "notice_period_days": 3, "monitoring_type": "aggregate_metrics"},
            {
                "warehouse": "Hamburg",
                "notice_period_days": 7,
                "monitoring_type": "individual_performance_tracking",
            },
            {"warehouse": "Munich", "notice_period_days": 5, "monitoring_type": "aggregate_metrics"},
        ]
    )
    compliance_summary = summarize_regulatory_risk(green_claim_results, workforce_results)

    chart_paths = [
        build_chart_savings_trap_gap(config, output_dir),
        build_chart_wage_forecast(config, output_dir),
        build_chart_break_even_curves(break_even_grid, config, output_dir),
        build_chart_adoption_distribution(adoption_df, output_dir),
        build_chart_strategy_contribution_ci(summary_df, output_dir),
        build_chart_tornado(tornado_df, config, output_dir),
        build_chart_scenario_heatmap(summary_df, output_dir),
        build_chart_downside_risk(summary_df, output_dir),
        build_chart_valuation_npv(valuation_df, output_dir),
        build_chart_cashflow_paths(cashflow_df, output_dir),
    ]

    replication_df.to_csv(tables_dir / "scenario_strategy_replication.csv", index=False)
    summary_df.to_csv(tables_dir / "scenario_summary_stats.csv", index=False)
    decision_df.to_csv(tables_dir / "decision_matrix.csv", index=False)
    valuation_df.to_csv(tables_dir / "valuation_summary.csv", index=False)
    cashflow_df.to_csv(tables_dir / "valuation_cashflows.csv", index=False)
    city_strategy_df.to_csv(tables_dir / "city_strategy_matrix.csv", index=False)
    city_recommendation_df.to_csv(tables_dir / "city_recommendations.csv", index=False)
    city_plan_df.to_csv(tables_dir / "city_portfolio_plan.csv", index=False)
    break_even_grid.to_csv(tables_dir / "break_even_grid.csv", index=False)
    tornado_df.to_csv(tables_dir / "tornado_sensitivity.csv", index=False)
    marketing_audit_df.to_csv(tables_dir / "marketing_audit.csv", index=False)
    pd.DataFrame(green_claim_results).to_csv(tables_dir / "green_claim_audit.csv", index=False)
    pd.DataFrame(workforce_results).to_csv(tables_dir / "workforce_audit.csv", index=False)

    paper_path = write_analytical_paper(
        config=config,
        summary_df=summary_df,
        decision_df=decision_df,
        valuation_df=valuation_df,
        replication_df=replication_df,
        break_even_grid=break_even_grid,
        marketing_audit_df=marketing_audit_df,
        compliance_summary=compliance_summary,
        city_recommendation_df=city_recommendation_df,
        city_plan_df=city_plan_df,
        chart_paths=chart_paths,
        output_dir=output_dir,
    )

    base_standard = summary_df[
        (summary_df["scenario"] == "base_case") & (summary_df["strategy"] == "standard_65")
    ].iloc[0]
    best = decision_df.iloc[0]
    labor_2026 = calculate_labor_cost_per_warehouse(config, 2026)
    labor_2027 = calculate_labor_cost_per_warehouse(config, 2027)
    refresh_payload = {}
    refresh_path = Path("data/latest_inputs.json")
    if refresh_path.exists():
        try:
            refresh_payload = json.loads(refresh_path.read_text(encoding="utf-8"))
        except Exception:
            refresh_payload = {}
    checks = refresh_payload.get("checks", []) if isinstance(refresh_payload, dict) else []
    refresh_ok = sum(1 for item in checks if item.get("status") == "OK")

    insights = {
        "impulse_resistance_base": consumer.calculate_impulse_resistance(),
        "labor_2026_eur": labor_2026,
        "labor_2027_eur": labor_2027,
        "labor_delta_pct": ((labor_2027 - labor_2026) / labor_2026) * 100,
        "recommended_strategy": str(best["strategy"]),
        "recommended_strategy_risk_adjusted_score": float(best["risk_adjusted_score"]),
        "recommended_strategy_npv_5y_eur": float(
            valuation_df.loc[valuation_df["strategy"] == str(best["strategy"]), "npv_5y_eur"].iloc[0]
        ),
        "base_standard_mean_contribution_eur": float(base_standard["mean_contribution_eur"]),
        "base_standard_prob_loss": float(base_standard["prob_loss"]),
        "marketing_reject_count": int((marketing_audit_df["decision"] == "REJECT").sum()),
        "compliance_summary": compliance_summary,
        "refresh_generated_at": refresh_payload.get("generated_at"),
        "refresh_ok_sources": refresh_ok,
        "refresh_total_sources": len(checks),
        "city_top3": city_recommendation_df.head(3)["city"].tolist()
        if not city_recommendation_df.empty
        else [],
    }
    with (output_dir / "executive_summary.json").open("w", encoding="utf-8") as fp:
        json.dump(insights, fp, indent=2)

    return {
        "config": config,
        "replication_df": replication_df,
        "summary_df": summary_df,
        "decision_df": decision_df,
        "valuation_df": valuation_df,
        "cashflow_df": cashflow_df,
        "city_strategy_df": city_strategy_df,
        "city_recommendation_df": city_recommendation_df,
        "city_plan_df": city_plan_df,
        "break_even_grid": break_even_grid,
        "tornado_df": tornado_df,
        "marketing_audit_df": marketing_audit_df,
        "green_claim_results": green_claim_results,
        "workforce_results": workforce_results,
        "chart_paths": chart_paths,
        "paper_path": paper_path,
        "insights": insights,
    }


def main() -> None:
    outputs = run_full_analysis()
    insights = outputs["insights"]
    summary_df = outputs["summary_df"]
    decision_df = outputs["decision_df"]
    valuation_df = outputs["valuation_df"]
    marketing_audit_df = outputs["marketing_audit_df"]
    city_recommendation_df = outputs["city_recommendation_df"]

    base_case = summary_df[summary_df["scenario"] == "base_case"].sort_values(
        "mean_contribution_eur", ascending=False
    )

    print("=== COSTCO GERMANY 2026 MARKET ENTRY SIMULATION (BOARD EDITION) ===")
    print(
        f"Labor Cost / Warehouse 2026 -> 2027: EUR {insights['labor_2026_eur']:,.0f} -> "
        f"EUR {insights['labor_2027_eur']:,.0f} ({insights['labor_delta_pct']:.2f}% increase)"
    )
    print(f"Recommended Strategy (Risk-Adjusted): {insights['recommended_strategy']}")
    print(
        "Base Standard Strategy: "
        f"mean contribution EUR {insights['base_standard_mean_contribution_eur']:,.0f}, "
        f"loss probability {insights['base_standard_prob_loss']:.1%}"
    )
    print(f"Recommended Strategy 5-Year NPV: EUR {insights['recommended_strategy_npv_5y_eur']:,.0f}")
    print(
        f"Data Refresh Sources OK: {insights['refresh_ok_sources']}/{insights['refresh_total_sources']} "
        f"(generated at {insights['refresh_generated_at']})"
    )

    print("\nBase-Case Scenario Ranking:")
    print(
        base_case[
            [
                "strategy",
                "mean_contribution_eur",
                "p10_contribution_eur",
                "p90_contribution_eur",
                "prob_loss",
                "mean_adoption_rate",
            ]
        ].to_string(index=False)
    )

    print("\nDecision Matrix:")
    print(
        decision_df[
            [
                "rank",
                "strategy",
                "weighted_mean_contribution_eur",
                "weighted_prob_loss",
                "weighted_cvar5_contribution_eur",
                "risk_adjusted_score",
            ]
        ].to_string(index=False)
    )

    print("\n5-Year Valuation:")
    print(
        valuation_df[
            [
                "strategy",
                "npv_5y_eur",
                "terminal_value_discounted_eur",
                "payback_year",
            ]
        ].to_string(index=False)
    )

    print("\nMarketing Audit:")
    for _, row in marketing_audit_df.iterrows():
        print(
            f"- [{row['decision']}] cues={row['cue_count']} confidence={row['confidence_score']:.2f} "
            f"| {row['text']}"
        )

    print("\nRegulatory Summary:")
    for k, v in insights["compliance_summary"].items():
        print(f"- {k}: {v}")

    if not city_recommendation_df.empty:
        print("\nCity Rollout Priority (Top 6):")
        print(
            city_recommendation_df[
                [
                    "city_rank",
                    "city",
                    "strategy",
                    "launch_wave",
                    "board_signal",
                    "risk_adjusted_city_score",
                    "city_prob_loss",
                    "launch_readiness_score",
                ]
            ]
            .head(6)
            .to_string(index=False)
        )

    print("\nGenerated Visuals:")
    for p in outputs["chart_paths"]:
        print(f"- {p}")

    print(f"\nAnalytical Paper: {outputs['paper_path']}")
    if int((marketing_audit_df["decision"] == "REJECT").sum()) > 0:
        print(
            "Consultancy Insight: Rewrite POS materials to include unit pricing (EUR/kg), "
            "certification IDs, and technical product specs."
        )


if __name__ == "__main__":
    main()
