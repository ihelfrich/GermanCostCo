"""Central configuration for the Costco Germany 2026 simulation."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


MARKET_CONFIG: Dict[str, Any] = {
    "meta": {
        "model_name": "Costco Germany 2026 Market Entry Simulation Engine",
        "as_of_date": "2026-02-13",
        "currency": "EUR",
        "version": "2.0.0",
    },
    "macro": {
        "consumer_climate_index": -24.1,  # Source: NIM/GfK (Jan 28, 2026 release; Feb 2026 outlook)
        "savings_rate_percent": 20.0,  # Source: Destatis gross household savings rate for Germany (2024)
        "savings_rate_net_percent": 10.3,  # Source: Destatis net household savings rate (H1 2025)
        "inflation_percent": 2.2,  # Source: European Commission Autumn 2025 forecast table for Germany (2026)
        "real_retail_growth_percent": 2.7,  # Source: Destatis annual retail turnover, 2025 real growth
    },
    "cultural": {
        "uncertainty_avoidance": 65,  # Source: Hofstede
        "long_term_orientation": 83,  # Source: Hofstede
        "indulgence": 40,  # Source: Hofstede
    },
    "labor_legal": {
        "min_wage_2026_eur_per_hour": 13.90,  # Source: BMAS Mindestlohnverordnung
        "min_wage_2027_eur_per_hour": 14.60,  # Source: BMAS Mindestlohnverordnung
        "empco_directive_deadline": "2026-09-27",  # Source: EmpCo timeline in prompt
        "standard_german_ad_information_cues_min": 7,  # Model standard informed by info-content literature.
        "us_ad_information_cues_typical": 3,  # Legacy benchmark for lower-information creative style.
    },
    "benchmarks": {
        "us_indulgence_reference": 68,  # Source: user-provided reference for charting
    },
    "operational_assumptions": {
        # Assumption: representative warehouse staffing baseline for first-year entry model.
        "employees_per_warehouse": 260,
        # Assumption: annual paid hours after leave/holiday norms.
        "hours_per_employee_per_year": 1780,
        # Assumption: fixed occupancy/utilities/logistics overhead per warehouse, annualized.
        "annual_fixed_opex_eur": 7_500_000,
        # Assumption: average gross margin on merchandise.
        "merchandise_gross_margin_percent": 12.5,
    },
    "demand_assumptions": {
        # Assumption: addressable households served by one warehouse catchment.
        "addressable_households": 450_000,
        # Assumption: annual household spend at a warehouse follows a lognormal-like shape.
        "yearly_spend_distribution_mean_eur": 4_800,
        "yearly_spend_distribution_sigma": 0.55,
        # Assumption: base merchandise discount range Costco can sustain in Germany.
        "bulk_discount_distribution_min": 0.06,
        "bulk_discount_distribution_mode": 0.10,
        "bulk_discount_distribution_max": 0.14,
        # Assumption: conversion elasticity to price/value.
        "membership_fee_sensitivity": 0.018,
    },
    "competition_assumptions": {
        # Source: EHI press release (Sep 2, 2025) - discounter share approx. 47%.
        "discounter_market_share_percent": 47.0,
        # Source context: Bundeskartellamt food-retail concentration statements.
        "top4_market_concentration_percent": 85.0,
        # Assumption: baseline share of contribution at risk from competitor response.
        "competitor_response_base_percent": 1.2,
        # Assumption: additional downside scenario uplift to price-pressure response.
        "downside_response_uplift_percent": 1.0,
        # Assumption: monthly tactical pricing volatility translated to annualized effect.
        "response_volatility_percent": 0.7,
    },
    "strategy_options": {
        "standard_65": {
            "membership_fee_eur": 65.0,
            "first_year_subsidy_eur": 0.0,
            "incremental_marketing_info_cues": 0,
        },
        "entry_35": {
            "membership_fee_eur": 35.0,
            "first_year_subsidy_eur": 0.0,
            "incremental_marketing_info_cues": 1,
        },
        "subsidized_65_to_20": {
            "membership_fee_eur": 65.0,
            "first_year_subsidy_eur": 45.0,
            "incremental_marketing_info_cues": 2,
        },
    },
    "simulation": {
        "n_households_monte_carlo": 15000,
        "random_seed": 42,
        "n_replications": 80,
    },
    "financial_assumptions": {
        # Assumption: weighted average cost of capital for Germany greenfield retail.
        "wacc_percent": 8.5,
        "terminal_growth_percent": 1.5,
        # Assumption: strategy horizon used in board capital-allocation reviews.
        "planning_horizon_years": 5,
        # Assumption: all-in capex per new warehouse (land, build, systems, launch).
        "capex_per_new_warehouse_eur": 55_000_000,
        # Assumption: ongoing maintenance capex burden as share of contribution.
        "maintenance_capex_percent_of_contribution": 8.0,
        # Board hurdle for contribution per warehouse in year 1.
        "contribution_hurdle_eur": 2_000_000,
        # Assumption: expected cumulative warehouse rollout over years 1..5.
        "warehouses_cumulative_by_year": [1, 2, 4, 6, 8],
        # Scenario probabilities used for risk-weighted expected value.
        "scenario_probabilities": {
            "base_case": 0.5,
            "downside_stress": 0.3,
            "upside_recovery": 0.2,
        },
    },
    "portfolio_budget_assumptions": {
        # Assumption: annual capex budget envelope for Germany rollout years 1..5.
        "annual_capex_budget_eur": [70_000_000, 120_000_000, 180_000_000, 220_000_000, 260_000_000],
        # Assumption: reserve kept for contingencies and inflation surprises.
        "budget_reserve_ratio": 0.10,
    },
    "portfolio_optimization_constraints": {
        # Hard rollout limits per year (new city launches).
        "max_new_cities_per_year": [1, 2, 3, 3, 3],
        # Hard cap on average modeled loss probability of launched cities per year.
        "annual_loss_risk_cap": [0.20, 0.24, 0.28, 0.32, 0.35],
        # Hard minimum geographic diversification in first 3 years.
        "min_distinct_states_first3_years": 3,
        # Objective shaping terms (EUR-equivalent).
        "readiness_bonus_per_point_eur": 60_000,
        "risk_penalty_per_loss_prob_point_eur": 2_200_000,
        "break_even_penalty_per_eur_over_70_monthly": 12_000,
    },
    "city_portfolio_assumptions": [
        # Index values are normalized around 1.0 (income) and [0,1] (fit/competition/logistics/regulatory).
        {"city": "Berlin", "state": "Berlin", "lat": 52.5200, "lon": 13.4050, "households_k": 2100, "income_index": 0.98, "brand_fit_index": 0.83, "logistics_index": 0.93, "competition_intensity": 0.76, "regulatory_complexity": 0.78, "savings_pressure_index": 0.67},
        {"city": "Hamburg", "state": "Hamburg", "lat": 53.5511, "lon": 9.9937, "households_k": 1080, "income_index": 1.07, "brand_fit_index": 0.81, "logistics_index": 0.92, "competition_intensity": 0.69, "regulatory_complexity": 0.66, "savings_pressure_index": 0.62},
        {"city": "Munich", "state": "Bavaria", "lat": 48.1351, "lon": 11.5820, "households_k": 900, "income_index": 1.18, "brand_fit_index": 0.89, "logistics_index": 0.90, "competition_intensity": 0.74, "regulatory_complexity": 0.71, "savings_pressure_index": 0.56},
        {"city": "Cologne", "state": "North Rhine-Westphalia", "lat": 50.9375, "lon": 6.9603, "households_k": 650, "income_index": 1.01, "brand_fit_index": 0.78, "logistics_index": 0.88, "competition_intensity": 0.73, "regulatory_complexity": 0.65, "savings_pressure_index": 0.61},
        {"city": "Frankfurt", "state": "Hesse", "lat": 50.1109, "lon": 8.6821, "households_k": 450, "income_index": 1.22, "brand_fit_index": 0.87, "logistics_index": 0.95, "competition_intensity": 0.68, "regulatory_complexity": 0.69, "savings_pressure_index": 0.58},
        {"city": "Stuttgart", "state": "Baden-Wuerttemberg", "lat": 48.7758, "lon": 9.1829, "households_k": 360, "income_index": 1.12, "brand_fit_index": 0.82, "logistics_index": 0.90, "competition_intensity": 0.70, "regulatory_complexity": 0.64, "savings_pressure_index": 0.57},
        {"city": "Duesseldorf", "state": "North Rhine-Westphalia", "lat": 51.2277, "lon": 6.7735, "households_k": 330, "income_index": 1.10, "brand_fit_index": 0.80, "logistics_index": 0.91, "competition_intensity": 0.75, "regulatory_complexity": 0.66, "savings_pressure_index": 0.60},
        {"city": "Leipzig", "state": "Saxony", "lat": 51.3397, "lon": 12.3731, "households_k": 320, "income_index": 0.93, "brand_fit_index": 0.74, "logistics_index": 0.84, "competition_intensity": 0.63, "regulatory_complexity": 0.58, "savings_pressure_index": 0.71},
        {"city": "Dortmund", "state": "North Rhine-Westphalia", "lat": 51.5136, "lon": 7.4653, "households_k": 310, "income_index": 0.94, "brand_fit_index": 0.72, "logistics_index": 0.86, "competition_intensity": 0.71, "regulatory_complexity": 0.60, "savings_pressure_index": 0.69},
        {"city": "Bremen", "state": "Bremen", "lat": 53.0793, "lon": 8.8017, "households_k": 220, "income_index": 0.97, "brand_fit_index": 0.70, "logistics_index": 0.85, "competition_intensity": 0.62, "regulatory_complexity": 0.57, "savings_pressure_index": 0.66},
        {"city": "Nuremberg", "state": "Bavaria", "lat": 49.4521, "lon": 11.0767, "households_k": 260, "income_index": 1.00, "brand_fit_index": 0.76, "logistics_index": 0.88, "competition_intensity": 0.67, "regulatory_complexity": 0.59, "savings_pressure_index": 0.63},
        {"city": "Hanover", "state": "Lower Saxony", "lat": 52.3759, "lon": 9.7320, "households_k": 280, "income_index": 0.99, "brand_fit_index": 0.75, "logistics_index": 0.89, "competition_intensity": 0.64, "regulatory_complexity": 0.58, "savings_pressure_index": 0.64},
    ],
    "regulatory_environment": [
        {
            "id": "empco_green_claims_2026",
            "category": "Marketing Claims",
            "regulation": "Directive (EU) 2024/825 (EmpCo amendments to UCPD)",
            "jurisdiction": "EU / Germany transposition",
            "requirement": (
                "Ban generic environmental claims without recognized excellent environmental performance, "
                "and ban product climate-neutral style claims based on offsetting outside the value chain."
            ),
            "effective_date": "2026-09-27",
            "deadline_or_trigger": "Member State transposition by 2026-03-27; application from 2026-09-27.",
            "maximum_sanction": "Penalties set by national transposition; treated as high legal exposure for claims.",
            "severity_score_1_to_5": 5,
            "likelihood_score_1_to_5": 4,
            "operational_owner": "Marketing + Legal",
            "source_url": "https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng",
            "source_note": "Article 4 deadlines and Annex I additions on generic and offset-based claims.",
        },
        {
            "id": "pangv_unit_pricing",
            "category": "Pricing Transparency",
            "regulation": "PAngV Section 4 + Section 20 with WiStrG 1954 Section 3",
            "jurisdiction": "Germany",
            "requirement": (
                "Consumer offers by weight/volume/length/area require clear unit-price display "
                "in addition to total price."
            ),
            "effective_date": "2022-05-28",
            "deadline_or_trigger": "Always-on obligation at point of sale and for price advertising.",
            "maximum_sanction": "Administrative fine up to EUR 25,000 (WiStrG Section 3(2)).",
            "severity_score_1_to_5": 4,
            "likelihood_score_1_to_5": 4,
            "operational_owner": "Commercial + Pricing Ops",
            "source_url": "https://www.gesetze-im-internet.de/pangv_2022/__4.html",
            "source_note": "Section 4 requires unit price; Section 20 links violations to WiStrG sanctions.",
        },
        {
            "id": "verpackg_registration",
            "category": "Packaging EPR",
            "regulation": "VerpackG Section 9 + Section 36",
            "jurisdiction": "Germany",
            "requirement": (
                "Register with the central authority before placing filled packaging on market; "
                "no sale enablement if manufacturer is not properly registered."
            ),
            "effective_date": "2019-01-01",
            "deadline_or_trigger": "Before first packaging is placed on the German market.",
            "maximum_sanction": "Administrative fines up to EUR 100,000 or EUR 200,000 depending offense.",
            "severity_score_1_to_5": 5,
            "likelihood_score_1_to_5": 3,
            "operational_owner": "Supply Chain + Legal",
            "source_url": "https://www.gesetze-im-internet.de/verpackg/__9.html",
            "source_note": "Section 9 registration and Section 36 penalty framework.",
        },
        {
            "id": "lksg_due_diligence",
            "category": "Supply Chain",
            "regulation": "LkSG Section 1 + Section 24",
            "jurisdiction": "Germany",
            "requirement": (
                "Human-rights and environmental due diligence program for in-scope companies; "
                "from 2024 threshold is >=1,000 domestic employees."
            ),
            "effective_date": "2024-01-01",
            "deadline_or_trigger": "Threshold reached and operations in scope.",
            "maximum_sanction": "Fines up to EUR 800,000 and up to 2% global turnover for very large entities.",
            "severity_score_1_to_5": 5,
            "likelihood_score_1_to_5": 3,
            "operational_owner": "Procurement + Compliance",
            "source_url": "https://www.gesetze-im-internet.de/lksg/__1.html",
            "source_note": "Section 1 scope threshold and Section 24 sanctions.",
        },
        {
            "id": "betrvg_codemination",
            "category": "Labor Governance",
            "regulation": "BetrVG Section 1 + Section 87",
            "jurisdiction": "Germany",
            "requirement": (
                "Works councils can be elected in establishments with >=5 permanent eligible employees; "
                "co-determination applies to scheduling and technical employee-monitoring systems."
            ),
            "effective_date": "1972-01-15",
            "deadline_or_trigger": "Applies once establishment structure and representation conditions exist.",
            "maximum_sanction": "Operational injunction/escalation risk via co-determination disputes.",
            "severity_score_1_to_5": 4,
            "likelihood_score_1_to_5": 4,
            "operational_owner": "HR + Operations",
            "source_url": "https://www.gesetze-im-internet.de/betrvg/__87.html",
            "source_note": "Section 1 establishment threshold and Section 87(1) nos. 2 and 6 powers.",
        },
        {
            "id": "arbzg_working_time",
            "category": "Labor Time Controls",
            "regulation": "ArbZG Section 3 + Section 22",
            "jurisdiction": "Germany",
            "requirement": (
                "Daily working time generally max 8 hours; up to 10 only if average returns to 8 "
                "within statutory balancing period."
            ),
            "effective_date": "1994-07-01",
            "deadline_or_trigger": "Always-on scheduling and recordkeeping compliance.",
            "maximum_sanction": "Administrative fines up to EUR 30,000 for key violations.",
            "severity_score_1_to_5": 4,
            "likelihood_score_1_to_5": 4,
            "operational_owner": "Warehouse Ops + HR",
            "source_url": "https://www.gesetze-im-internet.de/arbzg/__3.html",
            "source_note": "Section 3 working-time cap and Section 22 penalty provisions.",
        },
        {
            "id": "gdpr_bdsg_employee_data",
            "category": "Data Protection",
            "regulation": "GDPR Article 83 + BDSG Section 26",
            "jurisdiction": "EU / Germany",
            "requirement": (
                "Employee data processing must be necessary for employment purposes and proportionate; "
                "high-penalty GDPR regime applies to unlawful processing."
            ),
            "effective_date": "2018-05-25",
            "deadline_or_trigger": "Always-on for workforce analytics, monitoring, and CRM data handling.",
            "maximum_sanction": "GDPR administrative fines up to EUR 20m or 4% global turnover (whichever higher).",
            "severity_score_1_to_5": 5,
            "likelihood_score_1_to_5": 3,
            "operational_owner": "Data Governance + Legal",
            "source_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng",
            "source_note": "GDPR Article 83 fine tiers and BDSG Section 26 employee-data conditions.",
        },
        {
            "id": "milog_wage_enforcement",
            "category": "Wage Compliance",
            "regulation": "MiLoG Section 1 + Section 21 and BMAS MiLoV5 update",
            "jurisdiction": "Germany",
            "requirement": (
                "Pay at least statutory minimum wage; current federal update sets EUR 13.90 from 2026-01-01 "
                "and EUR 14.60 from 2027-01-01."
            ),
            "effective_date": "2026-01-01",
            "deadline_or_trigger": "Payroll compliance from each wage-step effective date.",
            "maximum_sanction": "Administrative fines up to EUR 500,000 for key wage-payment violations.",
            "severity_score_1_to_5": 5,
            "likelihood_score_1_to_5": 3,
            "operational_owner": "Payroll + HR",
            "source_url": "https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html",
            "source_note": "MiLoV5 rates and MiLoG Section 21 sanction levels.",
        },
        {
            "id": "eu_food_info_1169",
            "category": "Food Labeling",
            "regulation": "Regulation (EU) No 1169/2011 Article 9 and Article 15",
            "jurisdiction": "EU / Germany",
            "requirement": (
                "Mandatory food particulars must be presented and available pre-purchase; "
                "mandatory food information must appear in language easily understood in market Member State."
            ),
            "effective_date": "2014-12-13",
            "deadline_or_trigger": "Applies to own-label and imported packaged food assortment.",
            "maximum_sanction": "Enforced via national food-law sanctions and product withdrawal risk.",
            "severity_score_1_to_5": 4,
            "likelihood_score_1_to_5": 3,
            "operational_owner": "Private Label QA + Legal",
            "source_url": "https://eur-lex.europa.eu/eli/reg/2011/1169/oj/eng",
            "source_note": "Article 9 mandatory particulars and Article 15 language rules.",
        },
    ],
    "macro_scenarios": {
        # Base reflects provided point-in-time data.
        "base_case": {
            "consumer_climate_index": -24.1,
            "savings_rate_percent": 20.0,
            "inflation_percent": 2.2,
            "discount_shift": 0.0,
        },
        # Downside stress: weaker confidence, more precautionary savings, hotter prices.
        "downside_stress": {
            "consumer_climate_index": -30.0,
            "savings_rate_percent": 22.5,
            "inflation_percent": 3.5,
            "discount_shift": -0.012,
        },
        # Upside recovery: less cash-hoarding, moderate price pressure.
        "upside_recovery": {
            "consumer_climate_index": -16.0,
            "savings_rate_percent": 16.5,
            "inflation_percent": 1.8,
            "discount_shift": 0.008,
        },
    },
    "visual_theme": {
        # Swiss-style neutral base + red accent.
        "grey": "#6E6E6E",
        "light_grey": "#E7E7E7",
        "red": "#B71C1C",
        "bg": "#FAFAFA",
        "text": "#222222",
    },
    "sources": {
        "consumer_climate": {
            "source": "Nuremberg Institute for Market Decisions (NIM), GfK Consumer Climate",
            "url": "https://www.nim.org/en/consumer-climate/type/consumer-climate",
            "evidence": "Jan 28, 2026 release: Consumer Climate indicator expected at -24.1 for Feb 2026.",
        },
        "savings_rate_destatis": {
            "source": "Destatis (Federal Statistical Office of Germany)",
            "url": "https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html",
            "evidence": "Net savings rate 10.3% (H1 2025); gross savings rate 20.0% (2024).",
        },
        "inflation_forecast": {
            "source": "European Commission - Economic forecast for Germany",
            "url": "https://economy-finance.ec.europa.eu/economic-surveillance-eu-member-states/country-pages/germany/economic-forecast-germany_en",
            "evidence": "Indicator table shows inflation 2.2% for 2026.",
        },
        "retail_growth": {
            "source": "Destatis retail annual result",
            "url": "https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/02/PD26_038_45212.html",
            "evidence": "Real retail turnover in 2025: +2.7% year-on-year.",
        },
        "minimum_wage": {
            "source": "BMAS (Federal Ministry of Labour and Social Affairs)",
            "url": "https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html",
            "evidence": "EUR 13.90 from Jan 1, 2026; EUR 14.60 from Jan 1, 2027.",
        },
        "empco_directive": {
            "source": "Directive (EU) 2024/825 (EUR-Lex)",
            "url": "https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng",
            "evidence": "Transposition by Mar 27, 2026; application from Sep 27, 2026; generic green-claim restrictions.",
        },
        "works_council_codemination": {
            "source": "BetrVG Section 87 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/betrvg/__87.html",
            "evidence": "Co-determination on working-time arrangement and technical monitoring systems.",
        },
        "costco_membership_fee": {
            "source": "Costco 2025 Annual Report",
            "url": "https://s201.q4cdn.com/287523651/files/doc_financials/2025/ar/COST-Annual-Report-2025.pdf",
            "evidence": "US annual membership fee USD 65 for Gold Star and Business memberships.",
        },
        "ehi_discounter_shift": {
            "source": "EHI Retail Institute press release",
            "url": "https://www.ehi.org/presse/preisbewusstes-einkaufen-discounter-legen-zu/",
            "evidence": "2025 release highlights share gains of discounters and price-conscious shopping behavior.",
        },
        "oecd_germany_snapshot": {
            "source": "OECD Germany Economic Snapshot (Dec 2025)",
            "url": "https://www.oecd.org/en/topics/sub-issues/economic-surveys/germany-economic-snapshot.html",
            "evidence": "Growth and inflation outlook for 2026 used for scenario framing.",
        },
        "imf_article_iv_2025": {
            "source": "IMF Article IV Staff Concluding Statement (Nov 26, 2025)",
            "url": "https://www.imf.org/en/news/articles/2025/11/26/mcs-112625-germany-staff-concluding-statement-of-the-2025-article-iv-mission",
            "evidence": "Downside risk framing for Germany growth and inflation uncertainty.",
        },
        "pangv_unit_price": {
            "source": "PAngV Section 4 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/pangv_2022/__4.html",
            "evidence": "Unit price must be displayed clearly with total price for covered goods.",
        },
        "wistrg_pricing_fines": {
            "source": "WiStrG 1954 Section 3 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/wistrg_1954/__3.html",
            "evidence": "Pricing-rule offenses can be fined up to EUR 25,000.",
        },
        "verpackg_registration": {
            "source": "VerpackG Sections 9 and 36 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/verpackg/__9.html",
            "evidence": "Pre-market registration duty and penalty framework up to EUR 100,000 / EUR 200,000.",
        },
        "lksg_scope_and_fines": {
            "source": "LkSG Sections 1 and 24 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/lksg/__1.html",
            "evidence": "Applies from 1,000 employees (2024 step) with sanctions up to EUR 800,000 and 2% turnover.",
        },
        "arbzg_limits": {
            "source": "ArbZG Sections 3 and 22 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/arbzg/__3.html",
            "evidence": "8-hour daily cap (10-hour conditional extension) and fines up to EUR 30,000.",
        },
        "gdpr_fine_tiers": {
            "source": "GDPR Article 83 (EUR-Lex)",
            "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng",
            "evidence": "Administrative fines up to EUR 20m or 4% global annual turnover.",
        },
        "bdsg_employee_data": {
            "source": "BDSG Section 26 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/bdsg_2018/__26.html",
            "evidence": "Employee-data processing must be necessary and proportionate for employment purposes.",
        },
        "eu_food_info_1169": {
            "source": "Regulation (EU) No 1169/2011 Articles 9 and 15 (EUR-Lex)",
            "url": "https://eur-lex.europa.eu/eli/reg/2011/1169/oj/eng",
            "evidence": "Mandatory food particulars and market-language requirements for food information.",
        },
        "milog_fines": {
            "source": "MiLoG Section 21 (gesetze-im-internet)",
            "url": "https://www.gesetze-im-internet.de/milog/__21.html",
            "evidence": "Minimum-wage violations can be fined up to EUR 500,000.",
        },
    },
}


REFRESH_DATA_PATH = Path(__file__).resolve().parent / "data" / "latest_inputs.json"


def _merge_overrides(config: Dict[str, Any], overrides: Dict[str, Any]) -> None:
    """Recursively merge overrides into config in-place."""
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            _merge_overrides(config[key], value)
        else:
            config[key] = value


def load_config(use_refresh: bool = True) -> Dict[str, Any]:
    """
    Return a deep copy so callers do not mutate the source-of-truth config.

    If `data/latest_inputs.json` exists, apply validated overrides under `overrides`.
    """
    config = deepcopy(MARKET_CONFIG)
    if use_refresh and REFRESH_DATA_PATH.exists():
        try:
            payload = json.loads(REFRESH_DATA_PATH.read_text(encoding="utf-8"))
            overrides = payload.get("overrides", {})
            quality_gate = bool(payload.get("quality_gate_passed", False))
            if isinstance(overrides, dict) and quality_gate:
                _merge_overrides(config, overrides)
                config.setdefault("meta", {})["refresh_data_used"] = True
                config["meta"]["refresh_generated_at"] = payload.get("generated_at")
                config["meta"]["refresh_overrides_keys"] = sorted(overrides.keys())
            else:
                config.setdefault("meta", {})["refresh_data_used"] = False
                config["meta"]["refresh_generated_at"] = payload.get("generated_at")
                config["meta"]["refresh_rejected"] = True
        except Exception:
            config.setdefault("meta", {})["refresh_data_used"] = False

    # Keep base-case scenario aligned with active macro values unless explicitly overridden.
    base_case = config.get("macro_scenarios", {}).get("base_case", {})
    macro = config.get("macro", {})
    for key in ("consumer_climate_index", "savings_rate_percent", "inflation_percent"):
        if key in macro:
            base_case[key] = macro[key]
    return config
