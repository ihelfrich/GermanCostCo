# Costco Germany 2026 Market Entry Simulation: Executive Analytical Paper

**Model Version:** 2.0.0  
**As Of Date:** 2026-02-13  
**Generated:** 2026-02-16 01:42 UTC

## Executive Thesis
Costco's Germany problem is not whether value retail works. It is whether the U.S. membership model can survive a market where household uncertainty is elevated, savings behavior is structurally defensive, and information/compliance expectations are materially stricter.

**Primary recommendation:** Run a controlled pilot only; withhold national rollout capex until economics are recalibrated.

**Three board-level claims from this model run**
1. **Commercial design claim:** the standard fee architecture is structurally fragile in the current demand regime.
2. **Risk claim:** downside exposure is heavily strategy-dependent, not exogenous.
3. **Capital claim:** operating resilience is necessary but insufficient; capital pacing determines whether the thesis is investable.

**Current readout**
- Winning strategy in risk-adjusted ranking: `subsidized_65_to_20`
- Base-case standard expected contribution: EUR -3,340,129
- Base-case standard loss probability: 100.0%
- Recommended strategy weighted loss probability: 0.0%
- Recommended strategy 5-year NPV: EUR -159,379,779
- Data refresh status: Refresh payload found but rejected by quality gate; defaults retained (generated at 2026-02-13T04:48:00.628582+00:00).

## Data Foundation and Context
- Consumer Climate Index: -24.1 (Source: NIM/GfK)
- Household savings rate (gross / net): 20.0% / 10.3%
- Inflation forecast: 2.2% (Source: European Commission)
- Real retail growth: +2.7% (Source: Destatis)
- Cultural profile (Hofstede): UAI 65, LTO 83, Indulgence 40
- Minimum wage path: EUR 13.9 (2026) to EUR 14.6 (2027)
- Wage-driven annual labor inflation per warehouse (modeled): 5.04% (EUR 6,432,920 to EUR 6,756,880)

### Source Register
| id | source | url | evidence |
| --- | --- | --- | --- |
| consumer_climate | Nuremberg Institute for Market Decisions (NIM), GfK Consumer Climate | https://www.nim.org/en/consumer-climate/type/consumer-climate | Jan 28, 2026 release: Consumer Climate indicator expected at -24.1 for Feb 2026. |
| savings_rate_destatis | Destatis (Federal Statistical Office of Germany) | https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html | Net savings rate 10.3% (H1 2025); gross savings rate 20.0% (2024). |
| inflation_forecast | European Commission - Economic forecast for Germany | https://economy-finance.ec.europa.eu/economic-surveillance-eu-member-states/country-pages/germany/economic-forecast-germany_en | Indicator table shows inflation 2.2% for 2026. |
| retail_growth | Destatis retail annual result | https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/02/PD26_038_45212.html | Real retail turnover in 2025: +2.7% year-on-year. |
| minimum_wage | BMAS (Federal Ministry of Labour and Social Affairs) | https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html | EUR 13.90 from Jan 1, 2026; EUR 14.60 from Jan 1, 2027. |
| empco_directive | Directive (EU) 2024/825 (EUR-Lex) | https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng | Transposition by Mar 27, 2026; application from Sep 27, 2026; generic green-claim restrictions. |
| works_council_codemination | BetrVG Section 87 (gesetze-im-internet) | https://www.gesetze-im-internet.de/betrvg/__87.html | Co-determination on working-time arrangement and technical monitoring systems. |
| costco_membership_fee | Costco 2025 Annual Report | https://s201.q4cdn.com/287523651/files/doc_financials/2025/ar/COST-Annual-Report-2025.pdf | US annual membership fee USD 65 for Gold Star and Business memberships. |
| ehi_discounter_shift | EHI Retail Institute press release | https://www.ehi.org/presse/preisbewusstes-einkaufen-discounter-legen-zu/ | 2025 release highlights share gains of discounters and price-conscious shopping behavior. |
| oecd_germany_snapshot | OECD Germany Economic Snapshot (Dec 2025) | https://www.oecd.org/en/topics/sub-issues/economic-surveys/germany-economic-snapshot.html | Growth and inflation outlook for 2026 used for scenario framing. |
| imf_article_iv_2025 | IMF Article IV Staff Concluding Statement (Nov 26, 2025) | https://www.imf.org/en/news/articles/2025/11/26/mcs-112625-germany-staff-concluding-statement-of-the-2025-article-iv-mission | Downside risk framing for Germany growth and inflation uncertainty. |
| pangv_unit_price | PAngV Section 4 (gesetze-im-internet) | https://www.gesetze-im-internet.de/pangv_2022/__4.html | Unit price must be displayed clearly with total price for covered goods. |
| wistrg_pricing_fines | WiStrG 1954 Section 3 (gesetze-im-internet) | https://www.gesetze-im-internet.de/wistrg_1954/__3.html | Pricing-rule offenses can be fined up to EUR 25,000. |
| verpackg_registration | VerpackG Sections 9 and 36 (gesetze-im-internet) | https://www.gesetze-im-internet.de/verpackg/__9.html | Pre-market registration duty and penalty framework up to EUR 100,000 / EUR 200,000. |
| lksg_scope_and_fines | LkSG Sections 1 and 24 (gesetze-im-internet) | https://www.gesetze-im-internet.de/lksg/__1.html | Applies from 1,000 employees (2024 step) with sanctions up to EUR 800,000 and 2% turnover. |
| arbzg_limits | ArbZG Sections 3 and 22 (gesetze-im-internet) | https://www.gesetze-im-internet.de/arbzg/__3.html | 8-hour daily cap (10-hour conditional extension) and fines up to EUR 30,000. |
| gdpr_fine_tiers | GDPR Article 83 (EUR-Lex) | https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng | Administrative fines up to EUR 20m or 4% global annual turnover. |
| bdsg_employee_data | BDSG Section 26 (gesetze-im-internet) | https://www.gesetze-im-internet.de/bdsg_2018/__26.html | Employee-data processing must be necessary and proportionate for employment purposes. |
| eu_food_info_1169 | Regulation (EU) No 1169/2011 Articles 9 and 15 (EUR-Lex) | https://eur-lex.europa.eu/eli/reg/2011/1169/oj/eng | Mandatory food particulars and market-language requirements for food information. |
| milog_fines | MiLoG Section 21 (gesetze-im-internet) | https://www.gesetze-im-internet.de/milog/__21.html | Minimum-wage violations can be fined up to EUR 500,000. |

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
| hypothesis | evidence | verdict |
| --- | --- | --- |
| H1: Standard-fee entry is commercially fragile in current German conditions. | Base-case standard contribution EUR -3,340,129; loss probability 100.0%. | Supported |
| H2: Lower upfront fee friction is first-order, not marginal. | Base-case uplift vs standard: entry EUR 7,356,645; recommended EUR 13,027,383. | Supported |
| H3: Tail risk is strategy-controllable through membership design. | Weighted loss probability: standard 83.8% vs recommended 0.0%. | Supported |
| H4: Operating resilience alone is sufficient for rollout approval. | Recommended strategy 5-year NPV is EUR -159,379,779. | Rejected |

## Scenario Results
| scenario | strategy | mean_contribution_eur | p10_contribution_eur | p90_contribution_eur | prob_loss | mean_adoption_rate | mean_break_even_monthly_eur |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_case | standard_65 | -3,340,128.67 | -4,010,101.13 | -2,699,226.47 | 100.00 | 0.09 | 55.36 |
| base_case | entry_35 | 4,016,516.48 | 2,829,900.98 | 5,244,114.18 | 0.00 | 0.20 | 29.81 |
| base_case | subsidized_65_to_20 | 9,687,254.03 | 8,203,444.79 | 10,870,795.16 | 0.00 | 0.30 | 17.03 |
| downside_stress | standard_65 | -3,541,795.60 | -4,384,811.85 | -2,695,462.08 | 100.00 | 0.06 | 63.71 |
| downside_stress | entry_35 | 4,851,581.06 | 3,659,646.13 | 5,877,847.72 | 0.00 | 0.13 | 34.31 |
| downside_stress | subsidized_65_to_20 | 12,419,492.77 | 10,677,177.56 | 13,944,068.42 | 0.00 | 0.21 | 19.60 |
| upside_recovery | standard_65 | 677,403.66 | -337,547.31 | 1,662,514.30 | 18.75 | 0.20 | 51.05 |
| upside_recovery | entry_35 | 8,610,368.21 | 7,383,327.87 | 9,840,110.08 | 0.00 | 0.39 | 27.49 |
| upside_recovery | subsidized_65_to_20 | 13,527,818.10 | 12,169,489.94 | 14,760,855.35 | 0.00 | 0.56 | 15.71 |

## Decision Matrix (Cross-Scenario)
| rank | strategy | weighted_mean_contribution_eur | weighted_prob_loss | weighted_cvar5_contribution_eur | risk_adjusted_score |
| --- | --- | --- | --- | --- | --- |
| 1.00 | subsidized_65_to_20 | 11,275,038.46 | 0.00 | 8,881,019.59 | 10,831,325.89 |
| 2.00 | entry_35 | 5,185,806.20 | 0.00 | 3,247,978.44 | 4,802,201.55 |
| 3.00 | standard_65 | -2,597,122.28 | 83.75 | -3,798,008.69 | -5,707,689.77 |

## Capital Allocation View (5-Year)
| strategy | npv_5y_eur | terminal_value_discounted_eur | payback_year |
| --- | --- | --- | --- |
| subsidized_65_to_20 | -159,379,778.54 | 0.00 | -1.00 |
| entry_35 | -257,000,115.20 | 0.00 | -1.00 |
| standard_65 | -377,902,367.09 | 0.00 | -1.00 |

## Board Strategy Options (3+1)
| option | design | weighted_mean_contribution_eur | weighted_prob_loss | npv_5y_eur | board_call |
| --- | --- | --- | --- | --- | --- |
| A. Direct transfer (standard_65) | EUR 65 annual fee, no subsidy, baseline U.S.-style messaging. | -2597122.2812844776 | 83.75 | -377902367.0920895 | REJECT (tail risk and negative value destruction). |
| B. Entry tier (entry_35) | EUR 35 annual fee, low-friction membership onboarding. | 5185806.200314692 | 0.0 | -257000115.19674185 | VIABLE FALLBACK (commercially positive, weaker than top strategy). |
| C. Subsidized launch (subsidized_65_to_20) | EUR 65 list fee with first-year subsidy to reduce upfront resistance. | 11275038.464204935 | 0.0 | -159379778.5417326 | RECOMMENDED PILOT (best risk-adjusted operating economics). |
| D. Hybrid no-fee trial / day-pass pilot (proxy) | Localized no-fee or day-pass trial to reduce membership resistance in high-savings cohorts; designed as a learning option, not immediate national model. | Proxy range EUR 5,185,806 to 11,275,038 | Proxy <= 10% with strict spend-floor targeting | Proxy range EUR -257,000,115 to -159,379,779 | TEST AS OPTION (requires dedicated experiment design). |

**Inference note:** Option D is intentionally treated as a strategic learning option with proxy ranges inferred from modeled Option B and Option C economics. It is not yet a fully parameterized Monte Carlo strategy in this run.

## 5-Year Cash-Flow Projection Snapshot
| strategy | year | cumulative_warehouses | free_cash_flow_eur | discounted_fcf_eur |
| --- | --- | --- | --- | --- |
| subsidized_65_to_20 | 1.00 | 1.00 | -44,626,964.61 | -41,130,842.96 |
| subsidized_65_to_20 | 2.00 | 2.00 | -33,485,913.14 | -28,444,785.95 |
| subsidized_65_to_20 | 3.00 | 4.00 | -65,378,930.47 | -51,185,694.13 |
| subsidized_65_to_20 | 4.00 | 6.00 | -40,590,598.87 | -29,289,132.32 |
| subsidized_65_to_20 | 5.00 | 8.00 | -14,028,099.20 | -9,329,323.17 |
| entry_35 | 1.00 | 1.00 | -50,229,058.30 | -46,294,062.95 |
| entry_35 | 2.00 | 2.00 | -45,201,934.52 | -38,397,022.25 |
| entry_35 | 3.00 | 4.00 | -89,877,748.84 | -70,366,017.44 |
| entry_35 | 4.00 | 6.00 | -79,006,254.93 | -57,008,881.85 |
| entry_35 | 5.00 | 8.00 | -67,565,506.26 | -44,934,130.71 |
| standard_65 | 1.00 | 1.00 | -57,597,122.28 | -53,084,905.33 |
| standard_65 | 2.00 | 2.00 | -60,279,863.03 | -51,205,048.34 |
| standard_65 | 3.00 | 4.00 | -120,733,785.54 | -94,523,458.45 |
| standard_65 | 4.00 | 6.00 | -126,366,071.16 | -91,182,507.35 |
| standard_65 | 5.00 | 8.00 | -132,181,118.08 | -87,906,447.63 |

## Market, Competitive, and Consumer Reality
| dimension | signal | strategy_implication |
| --- | --- | --- |
| Discounter intensity | Discounters at ~47.0% share (model baseline). | Cost leadership pressure remains structural; Costco must win on basket transparency + trust. |
| Market concentration | Top-4 concentration modeled at ~85%. | Incumbents can retaliate quickly by region and category. |
| Consumer defensive posture | GfK/NIM climate -24.1 with savings rate 20.0% indicates elevated precautionary behavior. | Membership friction must be offset by visible and quantified savings evidence. |
| Price transparency requirement | German shoppers and law both require clear unit-price comparability (EUR/kg). | POS and digital copy must lead with concrete information cues and verifiable claims. |

## Regulatory Environment (Dedicated Board Tab Summary)
| effective_date | category | regulation | deadline_or_trigger | maximum_sanction | severity_score_1_to_5 | likelihood_score_1_to_5 | operational_owner | source_url |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-27 | Marketing Claims | Directive (EU) 2024/825 (EmpCo amendments to UCPD) | Member State transposition by 2026-03-27; application from 2026-09-27. | Penalties set by national transposition; treated as high legal exposure for claims. | 5.00 | 4.00 | Marketing + Legal | https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng |
| 2018-05-25 | Data Protection | GDPR Article 83 + BDSG Section 26 | Always-on for workforce analytics, monitoring, and CRM data handling. | GDPR administrative fines up to EUR 20m or 4% global turnover (whichever higher). | 5.00 | 3.00 | Data Governance + Legal | https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng |
| 2019-01-01 | Packaging EPR | VerpackG Section 9 + Section 36 | Before first packaging is placed on the German market. | Administrative fines up to EUR 100,000 or EUR 200,000 depending offense. | 5.00 | 3.00 | Supply Chain + Legal | https://www.gesetze-im-internet.de/verpackg/__9.html |
| 2024-01-01 | Supply Chain | LkSG Section 1 + Section 24 | Threshold reached and operations in scope. | Fines up to EUR 800,000 and up to 2% global turnover for very large entities. | 5.00 | 3.00 | Procurement + Compliance | https://www.gesetze-im-internet.de/lksg/__1.html |
| 2026-01-01 | Wage Compliance | MiLoG Section 1 + Section 21 and BMAS MiLoV5 update | Payroll compliance from each wage-step effective date. | Administrative fines up to EUR 500,000 for key wage-payment violations. | 5.00 | 3.00 | Payroll + HR | https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html |
| 1972-01-15 | Labor Governance | BetrVG Section 1 + Section 87 | Applies once establishment structure and representation conditions exist. | Operational injunction/escalation risk via co-determination disputes. | 4.00 | 4.00 | HR + Operations | https://www.gesetze-im-internet.de/betrvg/__87.html |
| 1994-07-01 | Labor Time Controls | ArbZG Section 3 + Section 22 | Always-on scheduling and recordkeeping compliance. | Administrative fines up to EUR 30,000 for key violations. | 4.00 | 4.00 | Warehouse Ops + HR | https://www.gesetze-im-internet.de/arbzg/__3.html |
| 2022-05-28 | Pricing Transparency | PAngV Section 4 + Section 20 with WiStrG 1954 Section 3 | Always-on obligation at point of sale and for price advertising. | Administrative fine up to EUR 25,000 (WiStrG Section 3(2)). | 4.00 | 4.00 | Commercial + Pricing Ops | https://www.gesetze-im-internet.de/pangv_2022/__4.html |
| 2014-12-13 | Food Labeling | Regulation (EU) No 1169/2011 Article 9 and Article 15 | Applies to own-label and imported packaged food assortment. | Enforced via national food-law sanctions and product withdrawal risk. | 4.00 | 3.00 | Private Label QA + Legal | https://eur-lex.europa.eu/eli/reg/2011/1169/oj/eng |

## Consumer Mindset and Cultural Differences
| signal | evidence | implication_for_costco |
| --- | --- | --- |
| Consumer climate regime | GfK/NIM consumer climate at -24.1. | Demand exists, but conversion requires stronger certainty and trust signals. |
| Precautionary savings behavior | Household savings rate 20.0% with inflation 2.2%. | Upfront fee friction must be neutralized with visible monthly savings logic. |
| Uncertainty avoidance | Hofstede UAI 65 (high). | Vague slogans underperform; prove quality, compliance, and unit economics explicitly. |
| Long-term orientation | Hofstede LTO 83 (high). | Value proposition should emphasize sustained annual savings, not one-off promotions. |
| Indulgence gap versus U.S. | Germany indulgence 40 vs U.S. reference 68. | Impulse and experiential framing should be secondary to rational, concrete benefits. |
| Information-density expectation | German copy expectation 7+ cues vs U.S. typical 3 (~2.33x density). | POS and digital assets require technical detail, unit pricing, certifications, and specs. |
| Observed marketing stress-test | 2/3 tested creatives rejected (66.7%) on cue density. | Creative governance must be treated as a conversion control system. |

### Commercial Translation Priorities
| priority_action | why_it_matters | owner |
| --- | --- | --- |
| Mandate unit-price-first messaging | Aligns with both legal expectation (PAngV) and consumer risk-reduction behavior. | Commercial + Pricing Ops |
| Adopt evidence-heavy copy templates | Raises conversion in high UAI context by replacing ambiguity with verifiable facts. | Marketing + Category |
| Reframe membership as monthly savings instrument | Translates annual fee into household budgeting language under savings pressure. | Membership + CRM |
| Publish compliance-by-design controls | Signals trust and reduces legal/operational friction in labor and claims governance. | Legal + HR + Operations |

## Mechanism Interpretation
1. **Fee friction is first-order:** moving from standard to entry fee improves base-case contribution by EUR 7,356,645; the recommended design improves by EUR 13,027,383.
2. **Risk is design-dependent:** weighted loss probability drops from 83.8% (standard) to 0.0% (recommended).
3. **Downside behavior is not uniform:** downside shock changes mean contribution by EUR -201,667 for standard vs EUR 2,732,239 for recommended.
4. **Commercial-to-capital gap remains:** despite strong operating contribution in all three scenarios (recommended strategy), 5-year NPV remains EUR -159,379,779.
5. **Conversion/compliance coupling is real:** 2/3 creatives fail cue thresholds (66.7%); high-severity compliance findings = 3.

## Strategic Paradox and Board Implication
The simulation produces a clear paradox: the recommended strategy generates superior operating economics (base: EUR 9,687,254; downside: EUR 12,419,493; upside: EUR 13,527,818) while failing current 5-year capital screens.

This means the board should not frame Germany as a binary go/no-go market thesis. It should frame Germany as a **real-options sequencing problem**:
1. Buy information through a tightly instrumented pilot.
2. Convert information into parameter updates (elasticity, competitor response, compliance defect rate).
3. Expand only when updated risk-adjusted economics clear threshold.

## Counterfactual Economics
| counterfactual | model_readout | board_implication |
| --- | --- | --- |
| Keep standard EUR 65 fee and scale nationally. | Weighted mean contribution EUR -2,597,122; weighted loss probability 83.8%. | High downside concentration; unacceptable risk-adjusted profile. |
| Use entry EUR 35 architecture as permanent base tier. | Weighted mean contribution EUR 5,185,806; base-case adoption 19.8%. | Viable intermediate option, but still inferior to recommended risk-adjusted score. |
| Deploy subsidized_65_to_20 with stage-gated investment. | Weighted mean contribution EUR 11,275,038; weighted loss probability 0.0%; 5-year NPV EUR -159,379,779. | Best operating profile; capital still requires option-value discipline. |

## Break-Even Geometry and Household Feasibility
- Median modeled break-even monthly spend: EUR 49.44
- P90 break-even monthly spend: EUR 107.12
- Share of fee/discount combinations above EUR 200/month: 0.8%
- Share above EUR 400/month: 0.0%
- Share above EUR 800/month: 0.0%

Interpretation: the barrier is not extreme monthly spend for most combinations; the strategic bottleneck is upfront fee friction and credibility of value communication.

## City Portfolio Optimization (Germany Rollout Geography)
The city layer translates strategy economics into a geographically staged launch plan by integrating catchment scale, competition intensity, logistics quality, regulatory friction, and savings-pressure behavior.
Rollout is constrained by annual capex envelopes (Y1: EUR 70,000,000, Y2: EUR 120,000,000, Y3: EUR 180,000,000, Y4: EUR 220,000,000, Y5: EUR 260,000,000) with a 10% reserve policy.

### Recommended Pilot Shortlist
- **Berlin (Berlin)**: strategy `subsidized_65_to_20`, score EUR 33,834,062, loss risk 0.0%, readiness 86.5/100.
- **Hamburg (Hamburg)**: strategy `subsidized_65_to_20`, score EUR 18,636,154, loss risk 0.0%, readiness 63.4/100.
- **Munich (Bavaria)**: strategy `subsidized_65_to_20`, score EUR 16,125,754, loss risk 0.0%, readiness 59.7/100.

### City-Level Priority Table
| city_rank | city | state | strategy | launch_wave | board_signal | risk_adjusted_city_score | expected_contribution_eur | city_prob_loss | adjusted_break_even_monthly_eur | capex_estimate_eur | rollout_year | launch_readiness_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.00 | Berlin | Berlin | subsidized_65_to_20 | Wave 2 Scale | GO | 33,834,062.39 | 33,834,062.39 | 0.00 | 21.55 | 68,101,000.00 | 2.00 | 86.50 |
| 2.00 | Hamburg | Hamburg | subsidized_65_to_20 | Wave 2 Scale | GO | 18,636,153.81 | 18,636,153.81 | 0.00 | 20.91 | 65,505,000.00 | 3.00 | 63.35 |
| 3.00 | Munich | Bavaria | subsidized_65_to_20 | Wave 2 Scale | GO | 16,125,754.33 | 16,125,754.33 | 0.00 | 20.47 | 67,078,000.00 | 3.00 | 59.66 |
| 4.00 | Cologne | North Rhine-Westphalia | subsidized_65_to_20 | Wave 3 Option | GO | 10,720,137.85 | 10,720,137.85 | 0.00 | 21.15 | 66,231,000.00 | 4.00 | 50.57 |
| 5.00 | Frankfurt | Hesse | subsidized_65_to_20 | Wave 3 Option | GO | 8,365,084.75 | 8,365,084.75 | 0.00 | 20.27 | 65,549,000.00 | 4.00 | 47.33 |
| 6.00 | Stuttgart | Baden-Wuerttemberg | subsidized_65_to_20 | Wave 3 Option | GO | 6,348,438.53 | 6,348,438.53 | 0.00 | 20.59 | 65,516,000.00 | 4.00 | 44.13 |
| 7.00 | Duesseldorf | North Rhine-Westphalia | subsidized_65_to_20 | Wave 3 Option | GO | 5,639,817.53 | 5,639,817.53 | 0.00 | 20.89 | 66,330,000.00 | 5.00 | 42.60 |
| 8.00 | Leipzig | Saxony | subsidized_65_to_20 | Wave 3 Option | GO | 5,176,290.54 | 5,176,290.54 | 0.00 | 21.52 | 64,339,000.00 | 5.00 | 42.07 |
| 9.00 | Dortmund | North Rhine-Westphalia | subsidized_65_to_20 | Wave 3 Option | GO | 4,907,139.12 | 4,907,139.12 | 0.00 | 21.62 | 65,417,000.00 | 5.00 | 41.24 |
| 10.00 | Hanover | Lower Saxony | subsidized_65_to_20 | Hold | GO | 4,716,311.37 | 4,716,311.37 | 0.00 | 21.10 | 63,965,000.00 | -1.00 | 41.44 |
| 11.00 | Nuremberg | Bavaria | subsidized_65_to_20 | Hold | GO | 4,355,123.73 | 4,355,123.73 | 0.00 | 21.11 | 64,581,000.00 | -1.00 | 40.86 |
| 12.00 | Bremen | Bremen | subsidized_65_to_20 | Hold | GO | 3,623,904.28 | 3,623,904.28 | 0.00 | 21.18 | 63,965,000.00 | -1.00 | 39.30 |

### Rollout Wave Summary
| launch_wave | strategy | city_count | mean_score | mean_expected_contribution_eur | mean_prob_loss | mean_capex_eur |
| --- | --- | --- | --- | --- | --- | --- |
| Hold | subsidized_65_to_20 | 3.00 | 4,231,779.80 | 4,231,779.80 | 0.00 | 64,170,333.33 |
| Wave 2 Scale | subsidized_65_to_20 | 3.00 | 22,865,323.51 | 22,865,323.51 | 0.00 | 66,894,666.67 |
| Wave 3 Option | subsidized_65_to_20 | 6.00 | 6,859,484.72 | 6,859,484.72 | 0.00 | 65,563,666.67 |

## 180-Day Operating Blueprint
| phase | time_window | core_deliverables | decision_metric |
| --- | --- | --- | --- |
| Phase 1: Pilot Design | 0-60 days | Two-city launch, cohort instrumentation, legal pre-clearance of green claims, works-council scheduling protocol. | Weekly contribution vs modeled P10/P50 corridor. |
| Phase 2: Learning and Recalibration | 60-120 days | Elasticity re-estimation, competitor response calibration, campaign cue-compliance enforcement. | Updated weighted loss probability and CVaR trend. |
| Phase 3: Investment Gate | 120-180 days | Board decision on expansion pace, capex resequencing, and membership architecture lock-in. | Rebased 5-year NPV and hurdle attainment probability. |

## Falsification Framework (What Would Invalidate This Recommendation)
| falsification_trigger | why_it_matters | action |
| --- | --- | --- |
| Pilot contribution underperforms modeled P10 corridor for 3 consecutive weeks. | Signals elasticity assumptions are optimistic or execution quality is insufficient. | Pause city expansion and re-estimate demand parameters before additional capex. |
| Conversion remains weak even after 7+ cue-compliant creative rollout. | Indicates value proposition mismatch beyond information density. | Redesign fee ladder and basket proposition; deprioritize media spend expansion. |
| High-severity compliance findings persist above threshold post-control deployment. | Legal and labor governance risk can destroy rollout option value. | Freeze operational scaling until compliance defect rate is reduced. |
| Recalibrated 5-year NPV remains negative after pilot learning integration. | Commercial performance fails to clear capital hurdle despite operational tuning. | Terminate national rollout thesis and revisit format design. |

## Visual Exhibits
- `outputs/chart_01_savings_trap_gap.png`
- `outputs/chart_02_wage_inflation_forecast.png`
- `outputs/chart_03_membership_sensitivity_curves.png`
- `outputs/chart_04_adoption_distribution.png`
- `outputs/chart_05_strategy_contribution_ci.png`
- `outputs/chart_06_tornado_sensitivity.png`
- `outputs/chart_07_scenario_heatmap.png`
- `outputs/chart_08_downside_risk.png`
- `outputs/chart_09_npv_by_strategy.png`
- `outputs/chart_10_cashflow_paths.png`

## Limitations and Research Agenda
1. **Elasticity uncertainty:** parameters remain assumption-driven until pilot microdata is integrated.
2. **Competitive response endogeneity:** Aldi/Lidl/Edeka reactions are approximated; city-level calibration required.
3. **Capital model simplification:** working-capital dynamics and cannibalization effects remain out-of-scope.
4. **Data refresh maturity:** automated refresh quality gate must improve before external decision-use.
5. **Next analytical step:** monthly Bayesian re-estimation loop tied to pilot telemetry and governance outcomes.
6. Supporting references and refresh protocol: `research/REAL_DATA_RESEARCH.md`; automation: `scripts/refresh_inputs.py`.
