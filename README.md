# Costco Germany 2026 Market Entry Simulation Engine

Board-grade analytical suite modeling the collision between Costco's U.S. model and German 2026 market constraints.

## Quick Start
```bash
python3 -m pip install -r requirements.txt
python3 scripts/refresh_inputs.py
MPLCONFIGDIR=/tmp/mpl python3 scenario_runner.py
python3 scripts/build_presentation_data.py
python3 -m http.server 8080
```

## Production-Style Run (Recommended)
```bash
python3 scripts/run_project.py --strict
python3 scripts/launch_presentation.py --port 8080
```

## Quality and Tests
```bash
python3 scripts/quality_gate.py --strict
python3 -m unittest discover -s tests -q
```

`scripts/refresh_inputs.py` includes an anomaly guard and quality gate.  
If the gate fails, defaults remain active and the report explicitly flags refresh rejection.

Open the board deck at:
- `http://localhost:8080/presentation/index.html`
- `http://localhost:8080/presentation/paper.html`
- `http://localhost:8080/presentation/regulatory.html`
- `http://localhost:8080/presentation/portfolio_map.html`

## React Consulting Portal (GitHub Pages Ready)
Interactive app for consulting-team use lives in `webapp/` and is deployed by GitHub Actions.

Local run:
```bash
pnpm install --dir webapp
python3 scripts/build_presentation_data.py
pnpm --dir webapp run prepare:data
pnpm --dir webapp run dev
```

Production build:
```bash
pnpm --dir webapp run build
pnpm --dir webapp run preview
```

Deployment workflow:
- `.github/workflows/deploy-pages.yml`
- Trigger: push to `main`
- GitHub repo setting: `Settings -> Pages -> Source = GitHub Actions`

Publish to your GitHub repo (`ihelfrich/GermanCostCo`):
```bash
git init
git branch -M main
git remote add origin https://github.com/ihelfrich/GermanCostCo.git
git add .
git commit -m "Build consulting portal with React + GitHub Pages CI"
git push -u origin main
```

## Modules
- `config_loader.py`: single source of truth for macro, cultural, labor/legal, and strategy assumptions.
- `consumer_psychology_model.py`: German consumer impulse resistance, information-cue audit, and adoption probability model.
- `compliance_engine.py`: EmpCo green-claim linting and workforce scheduling/monitoring risk checks.
- `scenario_runner.py`: Monte Carlo strategy simulation, sensitivity analyses, visualization, and analytical paper generation.
- `research/REAL_DATA_RESEARCH.md`: traceable external evidence register (official data, reports, literature links).
- `research/CONSULTING_PLAYBOOK.md`: hypothesis tree and consulting workplan.
- `research/MODEL_RISK_REGISTER.md`: model risks, mitigations, and controls.
- `scripts/refresh_inputs.py`: automated source refresh script that writes `data/latest_inputs.json`.
- `scripts/build_presentation_data.py`: builds `presentation/data/presentation_data.json` for the web deck.
- `scripts/quality_gate.py`: validates table integrity, payload integrity, and rollout consistency.
- `scripts/run_project.py`: one-command pipeline (simulate -> payload -> quality gate).
- `.github/workflows/deploy-pages.yml`: CI/CD pipeline for GitHub Pages deployment.
- `webapp/`: React/TypeScript portal (Executive, Regulatory, and City Map tabs).
- `presentation/index.html`: premium executive presentation with interactive charts.
- `presentation/regulatory.html`: dedicated regulatory-environment tab with legal risk timeline and control matrix.
- `presentation/portfolio_map.html`: Leaflet city-level portfolio and rollout optimization map.

## Generated Outputs
- Visuals: `outputs/chart_01_*.png` through `outputs/chart_10_*.png`
- Tables:
  - `outputs/tables/scenario_strategy_replication.csv`
  - `outputs/tables/scenario_summary_stats.csv`
  - `outputs/tables/decision_matrix.csv`
  - `outputs/tables/valuation_summary.csv`
  - `outputs/tables/valuation_cashflows.csv`
  - `outputs/tables/city_strategy_matrix.csv`
  - `outputs/tables/city_recommendations.csv`
  - `outputs/tables/city_portfolio_plan.csv`
  - `outputs/tables/break_even_grid.csv`
  - `outputs/tables/tornado_sensitivity.csv`
  - `outputs/tables/marketing_audit.csv`
  - `outputs/tables/green_claim_audit.csv`
  - `outputs/tables/workforce_audit.csv`
- Refresh payload: `data/latest_inputs.json`
- Executive JSON: `outputs/executive_summary.json`
- Full report: `outputs/Costco_Germany_2026_Analytical_Paper.md`

## Core Recommendation Logic
The engine ranks strategy options with a risk-adjusted score across macro scenarios using:
- Expected annual contribution
- Volatility penalty
- Downside-loss probability penalty
- Tail-risk penalty (CVaR)
- 5-year NPV/payback for capital-allocation relevance
