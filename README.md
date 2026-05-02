# Cricket Analysis Project

This repository now includes a small **ball-by-ball cricket analysis pipeline** built with Python and Pandas.

## Project Structure

- `src/cricket_analysis.py` — analysis functions and CLI entrypoint.
- `data/sample_deliveries.csv` — sample deliveries dataset.
- `outputs/` — generated result files (created when the script runs).

## What the analysis generates

The pipeline writes three CSV reports:

1. `batting_summary.csv` — runs, balls, boundaries, strike rate per batter.
2. `bowling_summary.csv` — wickets, economy, overs, strike rate per bowler.
3. `team_totals.csv` — innings-level team totals.

## Quickstart

```bash
python3 -m pip install -r requirements.txt
python3 src/cricket_analysis.py --input data/sample_deliveries.csv --output-dir outputs
```

## Custom data format

Your input CSV should include these columns:

- `match_id`, `innings`, `over`, `ball`
- `batting_team`, `bowling_team`
- `striker`, `bowler`
- `runs_off_bat`, `extras`, `wicket_type`

`wicket_type` can be blank when no wicket falls.
