# Group 4 Integration + Portfolio Output

Integrates Group 1 (Macro), Group 2 (Policy), and Group 3 (Earnings/AI) into a unified regional ranking and trade idea pipeline.

## How to run

    python3 main_model.py

## Generated outputs (in `outputs/`)

- `final_composite_score_table.csv`
- `regional_rankings.csv`
- `trade_ideas.csv`
- `summary_report.txt`
- `composite_scores_chart.png`
- `pillar_contributions_chart.png`

## Notes / Methodology

- **Standardization & Weighting:** Scales each pillar to a comparable **0-1 scale**. Applies a custom weight split: 30% Macro, 30% Policy, 20% Earnings, 20% AI.
- **Missing Data Handling:** Missing pillar values are assigned a neutral score of **0.5** to penalize without dropping the region entirely.
- **Pipeline Visibility:** Prints intermediate tables (via `tabulate`) to the console for easy pipeline debugging.
- **Trade Safeguards:** Execution includes a hard-stop warning, preventing trade generation if fewer than two regions have valid data.
- **Synchronized Charts:** The stacked pillar chart perfectly sums to the composite score chart, making them presentation-ready.