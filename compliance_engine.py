"""Regulatory linting for green claims and workforce governance."""

from __future__ import annotations

import re
from typing import Dict, List

# Source context: Generic environmental claims are banned under EmpCo from Sept 2026.
BANNED_GREEN_TERMS = ("climate neutral", "eco-friendly", "green")
ISO_CERT_PATTERN = re.compile(r"\bISO\s?\d{3,5}(?:-\d+)?\b", re.IGNORECASE)


def audit_green_claims(product_label_list: List[str]) -> List[Dict[str, str]]:
    """
    Flag generic green claims unless a verifiable ISO certification ID is present.
    """
    results: List[Dict[str, str]] = []
    for label in product_label_list:
        lowered = label.lower()
        matched_terms = [term for term in BANNED_GREEN_TERMS if term in lowered]
        has_iso_id = bool(ISO_CERT_PATTERN.search(label))

        if matched_terms and not has_iso_id:
            results.append(
                {
                    "label": label,
                    "status": "VIOLATION",
                    "severity": "HIGH",
                    "rule": "EmpCo Generic Green Claims Ban (effective Sept 27, 2026)",
                    "reason": (
                        f"Generic claim(s) {matched_terms} without verified ISO certification ID."
                    ),
                    "remediation": "Attach verifiable certification ID or remove generic claim language.",
                }
            )
        else:
            results.append(
                {
                    "label": label,
                    "status": "PASS",
                    "severity": "NONE",
                    "rule": "EmpCo Generic Green Claims Ban",
                    "reason": "No banned generic claim or claim substantiated by ISO ID.",
                    "remediation": "None required.",
                }
            )
    return results


def check_workforce_scheduling(shift_plan: List[Dict] | Dict) -> List[Dict]:
    """
    Audit scheduling/monitoring entries for works council and GDPR/Betriebsrat risks.

    Rules:
    - If notice_period < 4 days -> WORKS_COUNCIL_ALERT
    - If monitoring_type == individual_performance_tracking -> GDPR_BETRIEBSRAT_VIOLATION
    """
    records = shift_plan if isinstance(shift_plan, list) else [shift_plan]
    audit_results: List[Dict] = []

    for record in records:
        alerts = []
        severity = "NONE"
        notice_period = record.get("notice_period_days", record.get("notice_period", 0))
        monitoring_type = str(record.get("monitoring_type", "")).strip().lower()

        if notice_period < 4:
            alerts.append("WORKS_COUNCIL_ALERT")
            severity = "MEDIUM" if severity == "NONE" else severity
        if monitoring_type == "individual_performance_tracking":
            alerts.append("GDPR_BETRIEBSRAT_VIOLATION")
            severity = "HIGH"

        audit_results.append(
            {
                "record": record,
                "status": "PASS" if not alerts else "ALERT",
                "severity": severity,
                "alerts": alerts,
                "remediation": (
                    "Increase notice period to >= 4 days and switch to aggregate/non-identifiable KPIs."
                    if alerts
                    else "None required."
                ),
            }
        )

    return audit_results


def summarize_regulatory_risk(
    green_claim_audit: List[Dict[str, str]], workforce_audit: List[Dict]
) -> Dict[str, int]:
    """Aggregate compliance findings into board-level risk counts."""
    violations = sum(1 for item in green_claim_audit if item["status"] == "VIOLATION")
    workforce_alerts = sum(1 for item in workforce_audit if item["status"] == "ALERT")
    high_severity = sum(
        1
        for item in [*green_claim_audit, *workforce_audit]
        if str(item.get("severity", "")).upper() == "HIGH"
    )
    return {
        "green_claim_violations": violations,
        "workforce_alerts": workforce_alerts,
        "high_severity_findings": high_severity,
        "total_findings": violations + workforce_alerts,
    }
