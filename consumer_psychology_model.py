"""Consumer behavior model for German purchasing psychology."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from config_loader import load_config

try:
    import nltk
except Exception:  # pragma: no cover - optional dependency
    nltk = None


@dataclass
class MarketingEvaluation:
    cue_count: int
    decision: str
    matched_cues: List[str]
    confidence_score: float
    reason: str


class GermanConsumer:
    """Simulates key behavioral constraints in Germany's 2026 market context."""

    # Source context: German ads need high information density due to high uncertainty avoidance.
    INFO_CUE_THRESHOLD = 7

    # Source: Empirically common high-information cues in German retail copy.
    KEYWORDS = (
        "bio",
        "iso",
        "din",
        "tuv",
        "tuv-gepruft",
        "ce",
        "fsc",
        "ecolabel",
        "haccp",
        "guarantee",
        "warranty",
        "class",
        "energy",
        "eur/kg",
        "€/kg",
        "per kg",
        "g",
        "kg",
        "ml",
        "l",
        "specification",
        "protein",
        "fat",
        "kcal",
    )

    NUMBER_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\b")
    SPEC_PATTERN = re.compile(
        r"\b(?:\d+(?:[.,]\d+)?\s?(?:€|eur|%|kg|g|l|ml|w|v|kwh|cm|mm|m2|kcal)|"
        r"iso\s?\d{3,5}(?:-\d+)?|din\s?[a-z0-9-]+|energy\s?class\s?[a-g][+]{0,3})\b",
        re.IGNORECASE,
    )

    def __init__(self, config: Dict | None = None) -> None:
        self.config = config if config is not None else load_config()

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    def calculate_impulse_resistance(
        self, consumer_climate_override: Optional[float] = None, savings_rate_override: Optional[float] = None
    ) -> float:
        """
        Calculate impulse-buy resistance.

        Logic:
        - Base resistance increases with low indulgence and high long-term orientation.
        - If consumer climate < -20 and savings rate > 15, apply 1.5x Savings Trap Multiplier.
          Source context: Anadolu reporting household cash-hoarding behavior.
        """
        cultural = self.config["cultural"]
        macro = self.config["macro"]

        indulgence = cultural["indulgence"]
        uncertainty_avoidance = cultural["uncertainty_avoidance"]
        long_term_orientation = cultural["long_term_orientation"]
        consumer_climate = (
            macro["consumer_climate_index"]
            if consumer_climate_override is None
            else float(consumer_climate_override)
        )
        savings_rate = (
            macro["savings_rate_percent"] if savings_rate_override is None else float(savings_rate_override)
        )

        # Normalize to a compact score range centered near 1.0.
        indulgence_penalty = (100 - indulgence) / 100.0
        risk_penalty = uncertainty_avoidance / 100.0
        future_orientation_penalty = long_term_orientation / 100.0

        base_resistance = 0.7 + (0.7 * indulgence_penalty) + (0.3 * risk_penalty) + (
            0.25 * future_orientation_penalty
        )

        if consumer_climate < -20 and savings_rate > 15:
            base_resistance *= 1.5  # Savings Trap Multiplier

        return round(base_resistance, 3)

    def count_information_cues(self, text: str) -> MarketingEvaluation:
        """Count concrete information cues in ad copy via lightweight NLP/regex."""
        normalized = text.lower()

        # Optional tokenization with nltk when available (fallback remains regex-based).
        if nltk is not None:
            try:
                tokens = nltk.word_tokenize(normalized)
            except LookupError:
                tokens = re.findall(r"\b\w+(?:-\w+)?\b", normalized)
        else:
            tokens = re.findall(r"\b\w+(?:-\w+)?\b", normalized)

        matched_cues: List[str] = []

        number_hits = self.NUMBER_PATTERN.findall(normalized)
        matched_cues.extend(number_hits)

        spec_hits = [m.group(0) for m in self.SPEC_PATTERN.finditer(normalized)]
        matched_cues.extend(spec_hits)

        keyword_hits = [tok for tok in tokens if tok in self.KEYWORDS]
        matched_cues.extend(keyword_hits)

        cue_count = len(matched_cues)
        decision = "CONSIDER" if cue_count >= self.INFO_CUE_THRESHOLD else "REJECT"

        confidence_score = min(0.99, max(0.01, self._sigmoid((cue_count - self.INFO_CUE_THRESHOLD) / 1.6)))
        if decision == "REJECT":
            reason = "Too vague for high uncertainty-avoidance market norms."
        else:
            reason = "Sufficient concrete detail to reduce perceived purchase risk."

        return MarketingEvaluation(
            cue_count=cue_count,
            decision=decision,
            matched_cues=matched_cues,
            confidence_score=confidence_score,
            reason=reason,
        )

    def evaluate_marketing_copy(self, text: str) -> str:
        """
        Return REJECT if information cues < 7, else CONSIDER.
        """
        evaluation = self.count_information_cues(text)
        return evaluation.decision

    def estimate_membership_adoption_probability(
        self,
        yearly_spend_eur: float,
        membership_fee_eur: float,
        bulk_discount: float,
        info_cues: int,
        first_year_subsidy_eur: float = 0.0,
        consumer_climate_override: Optional[float] = None,
        savings_rate_override: Optional[float] = None,
    ) -> float:
        """
        Probabilistic adoption model (0..1) blending economics + psychology.

        Net_Benefit = (Yearly_Spend * Bulk_Discount) - Effective_Fee
        Effective_Fee = membership_fee - subsidy
        """
        effective_fee = max(0.0, membership_fee_eur - first_year_subsidy_eur)
        net_benefit = (yearly_spend_eur * bulk_discount) - effective_fee
        resistance = self.calculate_impulse_resistance(
            consumer_climate_override=consumer_climate_override,
            savings_rate_override=savings_rate_override,
        )

        fee_sensitivity = self.config["demand_assumptions"]["membership_fee_sensitivity"]
        info_density_boost = (info_cues - self.INFO_CUE_THRESHOLD) * 0.18
        economic_term = net_benefit / 220.0
        fee_term = -(effective_fee * fee_sensitivity)
        resistance_term = -0.85 * resistance

        latent_score = economic_term + info_density_boost + fee_term + resistance_term
        probability = self._sigmoid(latent_score)
        return float(max(0.0, min(1.0, probability)))
