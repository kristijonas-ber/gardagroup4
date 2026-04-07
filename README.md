# Group 4 Integration + Portfolio Output

This project brings together Group 1 macro, Group 2 policy, and Group 3 earnings/AI outputs into a single composite regional ranking and trade idea pipeline.

## Files

- `main_model.py` - New integration entrypoint for Group 4.
- `main.py` - Updated wrapper that delegates to `main_model.py`.
- `outputs/` - Generated outputs including final score table, rankings, trade ideas, charts, and summary report.

## How to run

From the project root:

```bash
python3 main.py
```

Or directly:

```bash
python3 main_model.py
```

## Generated outputs

- `outputs/final_composite_score_table.csv`
- `outputs/regional_rankings.csv`
- `outputs/trade_ideas.csv`
- `outputs/summary_report.txt`
- `outputs/composite_scores_chart.png`
- `outputs/pillar_contributions_chart.png`

## Notes

- `main_model.py` standardizes each input pillar to a comparable 0-100 scale.
- Missing pillar values are treated as neutral rather than dropped.
- The final composite score is weighted and adjusted for coverage.
- The charts are designed to be presentation-friendly for a deck.
