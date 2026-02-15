# Real-Data Research Dossier (Germany Entry 2026)

This dossier documents the external evidence used to calibrate and justify model inputs in this repository.

## 1) Macro & Market Inputs (Evidence Table)

| Variable | Model Value | Evidence | Source Link |
| --- | ---: | --- | --- |
| Consumer Climate Index (Germany) | -24.1 | NIM/GfK release on Jan 28, 2026 reports expected Feb 2026 level at -24.1. | https://www.nim.org/en/consumer-climate/type/consumer-climate |
| Household Savings Rate (gross) | 20.0% | Destatis reports Germany gross household savings rate at 20.0% in 2024. | https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html |
| Household Savings Rate (net) | 10.3% | Destatis reports net household savings rate at 10.3% in first half of 2025. | https://www.destatis.de/DE/Presse/Pressemitteilungen/2025/10/PD25_N059_81.html |
| Inflation (Germany, 2026) | 2.2% | European Commission Autumn 2025 Germany forecast table includes 2.2 for 2026 inflation. | https://economy-finance.ec.europa.eu/economic-surveillance-eu-member-states/country-pages/germany/economic-forecast-germany_en |
| Real Retail Growth (Germany, annual) | +2.7% | Destatis annual release for 2025 retail turnover in real terms: +2.7%. | https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/02/PD26_038_45212.html |

## 2) Labor, Regulatory, and Business Model Inputs

| Variable / Rule | Model Value | Evidence | Source Link |
| --- | --- | --- | --- |
| German minimum wage 2026 | EUR 13.90/hour | BMAS legal notice confirms effective Jan 1, 2026. | https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html |
| German minimum wage 2027 | EUR 14.60/hour | BMAS legal notice confirms effective Jan 1, 2027. | https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html |
| EmpCo application date | Sep 27, 2026 | Directive (EU) 2024/825: transposition by Mar 27, 2026; application from Sep 27, 2026. | https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng |
| Works council co-determination | Scheduling and technical monitoring are co-determined | BetrVG Section 87 includes working-time arrangement and technical monitoring provisions. | https://www.gesetze-im-internet.de/betrvg/__87.html |
| Costco base membership reference | USD 65 annual | Costco FY2025 annual report documents Gold Star/Business fee at USD 65. | https://s201.q4cdn.com/287523651/files/doc_financials/2025/ar/COST-Annual-Report-2025.pdf |

## 3) Literature Inputs (Peer-Reviewed / Academic)

The model uses light structural assumptions for marketing information density and uncertainty friction. The following literature underpins those modeling choices:

1. Abernethy, A. M., and Franke, G. R. (1996). *The Information Content of Advertising: A Meta-Analysis*. Journal of Advertising, 25(2), 1-17.  
   Link: https://www.tandfonline.com/doi/abs/10.1080/00913367.1996.10673500  
   Use in model: supports information-cue framing as a measurable conversion lever.

2. Hofstede, G., Hofstede, G. J., and Minkov, M. (2010). *Cultures and Organizations: Software of the Mind*. McGraw-Hill.  
   Use in model: uncertainty avoidance, long-term orientation, indulgence structure.

3. NIM/GfK consumer-climate publication stream (2026).  
   Link: https://www.nim.org/en/consumer-climate/type/consumer-climate  
   Use in model: links weak confidence and precautionary behavior to conversion drag.

## 4) Data Hygiene Notes

1. Savings rates differ by metric definition (gross vs net). The model carries both and uses gross savings as the "savings trap" behavioral trigger.
2. Inflation input is forecast-based for 2026 and should be refreshed quarterly.
3. Real retail growth is annual and backward-looking (2025) in current evidence; scenario stress tests handle forecast uncertainty.

## 5) Refresh Protocol

Before each strategy committee cycle:

1. Refresh NIM consumer climate.
2. Refresh Destatis household savings metrics and retail turnover.
3. Refresh EC/Bundesbank inflation projections.
4. Re-run `scenario_runner.py` and regenerate `outputs/Costco_Germany_2026_Analytical_Paper.md`.

## 6) Automation and Controls

1. Use `python3 scripts/refresh_inputs.py` to fetch and parse source pages.
2. Review `data/latest_inputs.json` for parser status and extraction errors.
3. Refresh overrides are only applied when the quality gate passes (critical metrics + minimum source success count).
4. If quality gate fails, defaults remain active and report output will state this explicitly.

## 7) Deep Regulatory Register (Primary-Law Sources)

This section underpins the dedicated `presentation/regulatory.html` tab.

| Domain | Legal Instrument | Concrete Rule Used in Model | Date / Threshold | Enforcement Envelope | Primary Source |
| --- | --- | --- | --- | --- | --- |
| Green claims / marketing | Directive (EU) 2024/825 (EmpCo) | Ban generic environmental claims without recognized excellent environmental performance; ban product climate-neutral style claims based on offsetting | Transposition by **2026-03-27**; application from **2026-09-27** | National penalties via Member State transposition | https://eur-lex.europa.eu/eli/dir/2024/825/oj/eng |
| Shelf and promo pricing | PAngV Sec. 4 + Sec. 20 + WiStrG Sec. 3 | Unit price must be shown clearly with total price for covered goods; violations mapped to economic offenses regime | In force | Up to **EUR 25,000** (WiStrG Sec. 3(2)) | https://www.gesetze-im-internet.de/pangv_2022/__4.html |
| Packaging EPR and market access | VerpackG Sec. 9 + Sec. 36 | Registration required before placing packaged goods on market; unregistered sale enablement prohibited | Pre-market requirement | Up to **EUR 100,000 / EUR 200,000** depending offense class | https://www.gesetze-im-internet.de/verpackg/__9.html |
| Supply chain due diligence | LkSG Sec. 1 + Sec. 24 | Applies at **>=1,000 domestic employees** from 2024; due-diligence program and reporting obligations | From **2024-01-01** threshold step | Up to **EUR 800,000** and up to **2%** global turnover for large entities | https://www.gesetze-im-internet.de/lksg/__1.html |
| Works council governance | BetrVG Sec. 1 + Sec. 87 | Works councils can be elected at >=5 permanent eligible employees; co-determination over scheduling and technical monitoring | Structural trigger by establishment | Co-determination deadlock/injunction risk | https://www.gesetze-im-internet.de/betrvg/__87.html |
| Working-time compliance | ArbZG Sec. 3 + Sec. 22 | 8-hour day default; extension to 10 only with balancing; enforcement tied to records and scheduling | Always-on | Up to **EUR 30,000** for key violations | https://www.gesetze-im-internet.de/arbzg/__3.html |
| Employee and customer data | GDPR Art. 83 + BDSG Sec. 26 | Employment-related data processing must be necessary/proportionate; high-penalty GDPR tiers | In force | Up to **EUR 20m** or **4%** global turnover | https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng |
| Wage compliance | MiLoG Sec. 1 + Sec. 21 and MiLoV5 | Statutory wage floor and documentation obligations; 2026/2027 federal step-up reflected in model | **EUR 13.90** (2026-01-01), **EUR 14.60** (2027-01-01) | Up to **EUR 500,000** for key underpayment offenses | https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/fuenfte-mindestlohnanpassungsverordnung-milov5.html |
| Food labeling and language | Regulation (EU) 1169/2011 Art. 9 + Art. 15 | Mandatory particulars and language understandable in market Member State for marketed food | In force (applies from 2014) | National food-law enforcement, withdrawal and labeling correction risk | https://eur-lex.europa.eu/eli/reg/2011/1169/oj/eng |

### Notes on legal interpretation
1. The model treats direct fine ceilings as directional severity calibrators, not expected-value fines.
2. Where EU directives require national transposition (EmpCo), the model flags high legal exposure even if national monetary penalty levels vary.
3. Labor-governance items (BetrVG, ArbZG, BDSG) are modeled as conversion and execution risks, not only legal costs, because they can stop rollout velocity.
