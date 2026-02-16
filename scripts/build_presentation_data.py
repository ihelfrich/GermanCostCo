#!/usr/bin/env python3
"""Build presentation-ready JSON payload from analysis outputs."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs"
TABLE_DIR = OUT_DIR / "tables"
PRESENTATION_DATA = ROOT / "presentation" / "data" / "presentation_data.json"
PRESENTATION_DATA_JS = ROOT / "presentation" / "data" / "presentation_data.js"
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config_loader import load_config


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _df_records(df: pd.DataFrame) -> List[Dict]:
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records"))


def _extract_eur_amounts(text: str) -> List[float]:
    raw = str(text or "")
    amounts: List[float] = []

    # Handles values like "EUR 800,000" or "EUR 25000".
    for token in re.findall(r"EUR\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+(?:\.[0-9]+)?)", raw, flags=re.IGNORECASE):
        cleaned = token.replace(",", "")
        try:
            amounts.append(float(cleaned))
        except ValueError:
            pass

    # Handles compact forms like "EUR 20m".
    for token in re.findall(r"EUR\s*([0-9]+(?:\.[0-9]+)?)\s*m\b", raw, flags=re.IGNORECASE):
        try:
            amounts.append(float(token) * 1_000_000)
        except ValueError:
            pass

    # Handles text forms like "EUR 20 million".
    for token in re.findall(r"EUR\s*([0-9]+(?:\.[0-9]+)?)\s*million\b", raw, flags=re.IGNORECASE):
        try:
            amounts.append(float(token) * 1_000_000)
        except ValueError:
            pass

    return amounts


def _build_regulatory_summary(rows: List[Dict]) -> Dict:
    if not rows:
        return {
            "count_total": 0,
            "count_high_severity": 0,
            "near_term_2026_2027": 0,
            "max_explicit_fine_eur": 0.0,
            "categories": {},
        }

    now = datetime(2026, 2, 15, tzinfo=timezone.utc)
    near_term_cutoff = datetime(2027, 12, 31, tzinfo=timezone.utc)
    high_sev = 0
    near_term = 0
    max_fine = 0.0
    categories: Dict[str, int] = {}

    for row in rows:
        sev = int(row.get("severity_score_1_to_5", 0))
        if sev >= 5:
            high_sev += 1

        category = str(row.get("category", "Uncategorized"))
        categories[category] = categories.get(category, 0) + 1

        eff = row.get("effective_date")
        if eff:
            try:
                eff_dt = datetime.fromisoformat(str(eff)).replace(tzinfo=timezone.utc)
                if now <= eff_dt <= near_term_cutoff:
                    near_term += 1
            except ValueError:
                pass

        for amount in _extract_eur_amounts(str(row.get("maximum_sanction", ""))):
            max_fine = max(max_fine, amount)

    return {
        "count_total": len(rows),
        "count_high_severity": high_sev,
        "near_term_2026_2027": near_term,
        "max_explicit_fine_eur": max_fine,
        "categories": categories,
    }


def build_payload() -> Dict:
    config = load_config()
    executive_summary = {}
    summary_path = OUT_DIR / "executive_summary.json"
    if summary_path.exists():
        executive_summary = json.loads(summary_path.read_text(encoding="utf-8"))

    decision_df = _safe_read_csv(TABLE_DIR / "decision_matrix.csv")
    scenario_df = _safe_read_csv(TABLE_DIR / "scenario_summary_stats.csv")
    valuation_df = _safe_read_csv(TABLE_DIR / "valuation_summary.csv")
    cashflow_df = _safe_read_csv(TABLE_DIR / "valuation_cashflows.csv")
    marketing_df = _safe_read_csv(TABLE_DIR / "marketing_audit.csv")
    green_df = _safe_read_csv(TABLE_DIR / "green_claim_audit.csv")
    workforce_df = _safe_read_csv(TABLE_DIR / "workforce_audit.csv")
    tornado_df = _safe_read_csv(TABLE_DIR / "tornado_sensitivity.csv")
    break_even_df = _safe_read_csv(TABLE_DIR / "break_even_grid.csv")
    city_strategy_df = _safe_read_csv(TABLE_DIR / "city_strategy_matrix.csv")
    city_reco_df = _safe_read_csv(TABLE_DIR / "city_recommendations.csv")
    city_plan_df = _safe_read_csv(TABLE_DIR / "city_portfolio_plan.csv")
    regulatory_rows = config.get("regulatory_environment", [])
    regulatory_summary = _build_regulatory_summary(regulatory_rows)

    chart_paths = sorted([str(p.relative_to(ROOT)) for p in OUT_DIR.glob("chart_*.png")])
    top_strategy = None
    if not decision_df.empty:
        top_strategy = str(decision_df.sort_values("rank").iloc[0]["strategy"])

    payload = {
        "meta": {
            "model_name": config.get("meta", {}).get("model_name"),
            "version": config.get("meta", {}).get("version"),
            "as_of_date": config.get("meta", {}).get("as_of_date"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "currency": config.get("meta", {}).get("currency", "EUR"),
        },
        "executive_summary": executive_summary,
        "key_decision": {
            "top_strategy": top_strategy,
            "top_strategy_npv": (
                float(valuation_df.sort_values("npv_5y_eur", ascending=False).iloc[0]["npv_5y_eur"])
                if not valuation_df.empty
                else None
            ),
            "is_stage_gated": bool(
                not valuation_df.empty and float(valuation_df["npv_5y_eur"].max()) < 0
            ),
        },
        "macro": config.get("macro", {}),
        "cultural": config.get("cultural", {}),
        "benchmarks": config.get("benchmarks", {}),
        "labor_legal": config.get("labor_legal", {}),
        "operational_assumptions": config.get("operational_assumptions", {}),
        "financial_assumptions": config.get("financial_assumptions", {}),
        "strategy_options": config.get("strategy_options", {}),
        "city_portfolio_assumptions": config.get("city_portfolio_assumptions", []),
        "regulatory_environment": regulatory_rows,
        "regulatory_summary": regulatory_summary,
        "sources": config.get("sources", {}),
        "decision_matrix": _df_records(decision_df),
        "scenario_summary": _df_records(scenario_df),
        "valuation_summary": _df_records(valuation_df),
        "valuation_cashflows": _df_records(cashflow_df),
        "marketing_audit": _df_records(marketing_df),
        "green_audit": _df_records(green_df),
        "workforce_audit": _df_records(workforce_df),
        "tornado_sensitivity": _df_records(tornado_df),
        "break_even_grid": _df_records(break_even_df),
        "city_strategy_matrix": _df_records(city_strategy_df),
        "city_recommendations": _df_records(city_reco_df),
        "city_portfolio_plan": _df_records(city_plan_df),
        "chart_paths": chart_paths,
    }
    return payload


def main() -> None:
    payload = build_payload()
    PRESENTATION_DATA.parent.mkdir(parents=True, exist_ok=True)
    PRESENTATION_DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # JS mirror enables `file://` usage where fetch() is often blocked by browser security.
    js_payload = "window.PRESENTATION_DATA = " + json.dumps(payload, indent=2) + ";\n"
    PRESENTATION_DATA_JS.write_text(js_payload, encoding="utf-8")
    print(f"Wrote presentation payload: {PRESENTATION_DATA}")
    print(f"Wrote presentation payload JS mirror: {PRESENTATION_DATA_JS}")


if __name__ == "__main__":
    main()
