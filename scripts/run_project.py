#!/usr/bin/env python3
"""Orchestrate full project pipeline: simulation, payload build, and quality gate."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Costco Germany full pipeline.")
    parser.add_argument("--skip-simulation", action="store_true", help="Skip scenario_runner execution")
    parser.add_argument("--strict", action="store_true", help="Fail on quality-gate violations")
    args = parser.parse_args()

    if not args.skip_simulation:
        run(["python3", "scenario_runner.py"])
    run(["python3", "scripts/build_presentation_data.py"])
    quality_cmd = ["python3", "scripts/quality_gate.py"]
    if args.strict:
        quality_cmd.append("--strict")
    run(quality_cmd)


if __name__ == "__main__":
    main()
