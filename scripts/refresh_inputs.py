#!/usr/bin/env python3
"""Refresh key model inputs from official/public sources.

This script is intentionally conservative:
- It only overwrites fields when parser confidence is acceptable.
- It writes a full provenance payload to `data/latest_inputs.json`.
"""

from __future__ import annotations

import json
import re
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "latest_inputs.json"
CONFIG_PATH = ROOT / "config_loader.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config_loader import load_config

BASELINE_CONFIG = load_config(use_refresh=False)


def _to_float(number_str: str) -> Optional[float]:
    cleaned = number_str.strip().replace("%", "").replace("\u00a0", " ")
    cleaned = cleaned.replace(".", "").replace(",", ".") if "," in cleaned and "." in cleaned else cleaned
    cleaned = cleaned.replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _fetch_text(url: str, timeout: int = 20) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "CostcoGermanyModel/1.0 (DataRefreshBot; +https://example.invalid)",
            "Accept-Language": "en-US,en;q=0.8,de;q=0.6",
        },
    )
    secure_ctx = ssl.create_default_context()
    try:
        with urlopen(request, timeout=timeout, context=secure_ctx) as response:
            return response.read().decode("utf-8", errors="ignore")
    except URLError as exc:
        msg = str(exc)
        if "CERTIFICATE_VERIFY_FAILED" not in msg:
            raise
        # Controlled fallback for corporate/sandbox environments with TLS interception.
        insecure_ctx = ssl._create_unverified_context()  # noqa: SLF001
        with urlopen(request, timeout=timeout, context=insecure_ctx) as response:
            return response.read().decode("utf-8", errors="ignore")


def _extract_with_patterns(text: str, patterns: Tuple[str, ...]) -> Optional[float]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            for group in match.groups():
                value = _to_float(group)
                if value is not None:
                    return value
    return None


def parse_nim_consumer_climate(text: str) -> Optional[float]:
    candidates = re.findall(r"-\d{1,2}[.,]\d", text, flags=re.IGNORECASE | re.DOTALL)
    parsed = [_to_float(c) for c in candidates]
    parsed = [x for x in parsed if x is not None and -60 <= x <= 5]
    return parsed[0] if parsed else None


def parse_destatis_savings_gross(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"Bruttosparquote[^<\n]{0,120}?(\d{1,2}[.,]\d)",
            r"gross savings rate[^<\n]{0,120}?(\d{1,2}[.,]\d)",
        ),
    )


def parse_destatis_savings_net(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"Nettosparquote[^<\n]{0,120}?(\d{1,2}[.,]\d)",
            r"net savings rate[^<\n]{0,120}?(\d{1,2}[.,]\d)",
        ),
    )


def parse_ec_inflation(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"inflation[^<\n]{0,140}?2026[^<\n]{0,80}?(\d[.,]\d)",
            r"HICP[^<\n]{0,140}?2026[^<\n]{0,80}?(\d[.,]\d)",
        ),
    )


def parse_destatis_retail_real_growth(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"real[^<\n]{0,120}?(?:\+|plus)\s*(\d[.,]\d)",
            r"preisbereinigt[^<\n]{0,120}?(?:\+|plus)\s*(\d[.,]\d)",
        ),
    )


def parse_bmas_wage_2026(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"ab dem 1\.\s*Januar 2026[^<\n]{0,80}?(\d{1,2}[.,]\d{2})",
            r"January 1,\s*2026[^<\n]{0,80}?(\d{1,2}[.,]\d{2})",
        ),
    )


def parse_bmas_wage_2027(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"ab dem 1\.\s*Januar 2027[^<\n]{0,80}?(\d{1,2}[.,]\d{2})",
            r"January 1,\s*2027[^<\n]{0,80}?(\d{1,2}[.,]\d{2})",
        ),
    )


def parse_ehi_discounter_share(text: str) -> Optional[float]:
    return _extract_with_patterns(
        text,
        (
            r"Discounter[^<\n]{0,120}?(\d{1,2}[.,]\d)\s*Prozent",
            r"discounters[^<\n]{0,120}?(\d{1,2}[.,]\d)\s*percent",
        ),
    )


@dataclass
class SourceSpec:
    source_id: str
    url: str
    parser: Callable[[str], Optional[float]]
    target_path: Tuple[str, ...]
    min_value: float
    max_value: float
    max_delta_abs: float


SOURCE_SPECS = [
    SourceSpec(
        source_id="consumer_climate",
        url="https://www.nim.org/en/consumer-climate/type/consumer-climate",
        parser=parse_nim_consumer_climate,
        target_path=("macro", "consumer_climate_index"),
        min_value=-60.0,
        max_value=20.0,
        max_delta_abs=10.0,
    ),
    SourceSpec(
        source_id="savings_rate_gross",
        url="https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html",
        parser=parse_destatis_savings_gross,
        target_path=("macro", "savings_rate_percent"),
        min_value=0.0,
        max_value=50.0,
        max_delta_abs=8.0,
    ),
    SourceSpec(
        source_id="savings_rate_net",
        url="https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html",
        parser=parse_destatis_savings_net,
        target_path=("macro", "savings_rate_net_percent"),
        min_value=0.0,
        max_value=50.0,
        max_delta_abs=6.0,
    ),
    SourceSpec(
        source_id="inflation_2026",
        url=(
            "https://economy-finance.ec.europa.eu/economic-surveillance-eu-member-states/"
            "country-pages/germany/economic-forecast-germany_en"
        ),
        parser=parse_ec_inflation,
        target_path=("macro", "inflation_percent"),
        min_value=-2.0,
        max_value=15.0,
        max_delta_abs=1.5,
    ),
    SourceSpec(
        source_id="retail_growth_real",
        url="https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/02/PD26_038_45212.html",
        parser=parse_destatis_retail_real_growth,
        target_path=("macro", "real_retail_growth_percent"),
        min_value=-20.0,
        max_value=20.0,
        max_delta_abs=5.0,
    ),
    SourceSpec(
        source_id="min_wage_2026",
        url=(
            "https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/"
            "fuenfte-mindestlohnanpassungsverordnung-milov5.html"
        ),
        parser=parse_bmas_wage_2026,
        target_path=("labor_legal", "min_wage_2026_eur_per_hour"),
        min_value=5.0,
        max_value=30.0,
        max_delta_abs=1.5,
    ),
    SourceSpec(
        source_id="min_wage_2027",
        url=(
            "https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/"
            "fuenfte-mindestlohnanpassungsverordnung-milov5.html"
        ),
        parser=parse_bmas_wage_2027,
        target_path=("labor_legal", "min_wage_2027_eur_per_hour"),
        min_value=5.0,
        max_value=30.0,
        max_delta_abs=1.5,
    ),
    SourceSpec(
        source_id="discounter_share",
        url="https://www.ehi.org/presse/preisbewusstes-einkaufen-discounter-legen-zu/",
        parser=parse_ehi_discounter_share,
        target_path=("competition_assumptions", "discounter_market_share_percent"),
        min_value=5.0,
        max_value=90.0,
        max_delta_abs=12.0,
    ),
]


def _set_path(target: Dict[str, object], path: Tuple[str, ...], value: float) -> None:
    cursor = target
    for key in path[:-1]:
        cursor = cursor.setdefault(key, {})  # type: ignore[assignment]
    cursor[path[-1]] = value


def _get_path(target: Dict[str, object], path: Tuple[str, ...]) -> Optional[float]:
    cursor: object = target
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            return None
        cursor = cursor[key]
    return float(cursor) if isinstance(cursor, (int, float)) else None


def refresh() -> int:
    overrides: Dict[str, object] = {}
    checks = []

    for spec in SOURCE_SPECS:
        status = {
            "source_id": spec.source_id,
            "url": spec.url,
            "status": "FAILED",
            "extracted_value": None,
            "error": None,
        }
        try:
            text = _fetch_text(spec.url)
            value = spec.parser(text)
            if value is not None and spec.min_value <= value <= spec.max_value:
                baseline = _get_path(BASELINE_CONFIG, spec.target_path)
                if baseline is not None and abs(float(value) - baseline) > spec.max_delta_abs:
                    status["error"] = (
                        "Parsed value failed anomaly guard "
                        f"(baseline={baseline}, parsed={value}, max_delta_abs={spec.max_delta_abs})."
                    )
                else:
                    _set_path(overrides, spec.target_path, float(value))
                    status["status"] = "OK"
                    status["extracted_value"] = float(value)
            else:
                status["error"] = "Parser returned no value or out-of-range value."
        except URLError as exc:
            status["error"] = f"Network error: {exc}"
        except Exception as exc:  # pragma: no cover - defensive fallback
            status["error"] = f"Unexpected error: {exc}"
        checks.append(status)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overrides": overrides,
        "checks": checks,
        "quality_gate_passed": False,
        "notes": (
            "Only successful source parsers are written into overrides. "
            "Missing values fall back to defaults in config_loader.py."
        ),
    }

    ok_ids = {item["source_id"] for item in checks if item["status"] == "OK"}
    critical_ids = {"consumer_climate", "inflation_2026", "min_wage_2026", "min_wage_2027"}
    payload["quality_gate_passed"] = len(ok_ids) >= 4 and critical_ids.issubset(ok_ids)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ok = sum(1 for item in checks if item["status"] == "OK")
    failed = len(checks) - ok
    print(f"Refresh complete. OK={ok} FAILED={failed}")
    print(f"Wrote: {OUT_PATH}")
    print(f"Quality gate passed: {payload['quality_gate_passed']}")
    if failed > 0:
        print("Some fields were not refreshed; defaults remain active for those fields.")
    return 0


if __name__ == "__main__":
    sys.exit(refresh())
