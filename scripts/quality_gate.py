#!/usr/bin/env python3
"""Project-wide quality gate for model configuration and generated outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "outputs" / "tables"
PRESENTATION_DATA = ROOT / "presentation" / "data" / "presentation_data.json"


def check(condition: bool, ok_msg: str, fail_msg: str, failures: List[str]) -> None:
    if condition:
        print(f"[OK]   {ok_msg}")
    else:
        print(f"[FAIL] {fail_msg}")
        failures.append(fail_msg)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def check_outputs(failures: List[str]) -> None:
    required_tables = [
        "scenario_summary_stats.csv",
        "decision_matrix.csv",
        "valuation_summary.csv",
        "city_recommendations.csv",
        "city_portfolio_plan.csv",
        "marketing_audit.csv",
    ]
    for table in required_tables:
        path = TABLE_DIR / table
        check(path.exists(), f"Table exists: {table}", f"Missing table: {table}", failures)
        if path.exists():
            df = pd.read_csv(path)
            check(len(df) > 0, f"Table has rows: {table}", f"Empty table: {table}", failures)


def check_decision_consistency(failures: List[str]) -> None:
    decision_df = _read_csv(TABLE_DIR / "decision_matrix.csv")
    valuation_df = _read_csv(TABLE_DIR / "valuation_summary.csv")
    if decision_df.empty or valuation_df.empty:
        return

    check(
        set(decision_df["strategy"]) == set(valuation_df["strategy"]),
        "Decision and valuation strategies aligned",
        "Strategy mismatch between decision and valuation outputs",
        failures,
    )


def check_city_plan(failures: List[str]) -> None:
    city_df = _read_csv(TABLE_DIR / "city_portfolio_plan.csv")
    if city_df.empty:
        return

    check(
        city_df["city"].nunique() == len(city_df),
        "City plan has unique city rows",
        "City plan has duplicate city rows",
        failures,
    )
    check(
        city_df["rollout_year"].isin([-1, 1, 2, 3, 4, 5]).all(),
        "Rollout year values valid",
        "Invalid rollout_year values detected",
        failures,
    )
    if "launch_wave" in city_df:
        valid_waves = {"Wave 1 Pilot", "Wave 2 Scale", "Wave 3 Option", "Hold"}
        check(
            city_df["launch_wave"].isin(valid_waves).all(),
            "Launch waves valid",
            "Invalid launch_wave labels detected",
            failures,
        )


def check_presentation_payload(failures: List[str]) -> None:
    check(
        PRESENTATION_DATA.exists(),
        "Presentation payload exists",
        "Missing presentation payload JSON",
        failures,
    )
    if not PRESENTATION_DATA.exists():
        return

    payload = json.loads(PRESENTATION_DATA.read_text(encoding="utf-8"))
    required_keys = [
        "decision_matrix",
        "valuation_summary",
        "scenario_summary",
        "city_recommendations",
        "city_portfolio_plan",
        "regulatory_environment",
        "regulatory_summary",
    ]
    for key in required_keys:
        check(key in payload, f"Payload key present: {key}", f"Missing payload key: {key}", failures)


def run_quality_gate(strict: bool = False) -> Tuple[bool, List[str]]:
    failures: List[str] = []

    print("=== Quality Gate: Costco Germany Simulation ===")
    check_outputs(failures)
    check_decision_consistency(failures)
    check_city_plan(failures)
    check_presentation_payload(failures)

    if failures:
        print("\nQuality Gate Result: FAILED")
        for item in failures:
            print(f"- {item}")
        return False, failures

    print("\nQuality Gate Result: PASSED")
    return True, failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Run quality gate checks on project outputs.")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero status on failures")
    args = parser.parse_args()

    ok, _ = run_quality_gate(strict=args.strict)
    if not ok and args.strict:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
