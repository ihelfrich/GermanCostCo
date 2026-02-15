# Executive Presentation

## Build Data Payload
```bash
python3 scripts/build_presentation_data.py
```

## Run Local Presentation Server
From project root:
```bash
python3 -m http.server 8080
```

Then open:
- `http://localhost:8080/presentation/index.html`
- `http://localhost:8080/presentation/paper.html`
- `http://localhost:8080/presentation/regulatory.html`
- `http://localhost:8080/presentation/portfolio_map.html`

The presentation is data-bound to model outputs in `outputs/` and `outputs/tables/`.
`scripts/build_presentation_data.py` now writes both:
- `presentation/data/presentation_data.json`
- `presentation/data/presentation_data.js` (for direct `file://` opening without local server)

## Open Directly From IDE (No Server)
You can open either HTML file directly from disk after building payload:
- `presentation/index.html`
- `presentation/paper.html`
- `presentation/regulatory.html`
- `presentation/portfolio_map.html`

## One-Command Launch
From project root:
```bash
python3 scripts/run_project.py --strict
python3 scripts/launch_presentation.py --port 8080
```

## What The Deck Includes
- Executive thesis cards with decision-critical claims.
- KPI ribbon and risk-adjusted strategy ranking.
- Scenario heatmap, downside probability, NPV and cash-flow charts.
- Launch readiness index (composite governance/economics score).
- Break-even contour surface (fee vs discount sensitivity).
- Compliance cards, evidence register, and stage-gated rollout roadmap.
- Dedicated regulatory tab with legal timeline, risk matrix, owner accountability, and full source-linked register.
- Leaflet city-portfolio map with launch waves, board-signal filters, and city ranking table.
- Print-ready styling for board-packet export.
