"""Simple cricket analytics utilities and CLI entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "match_id",
    "innings",
    "over",
    "ball",
    "batting_team",
    "bowling_team",
    "striker",
    "bowler",
    "runs_off_bat",
    "extras",
    "wicket_type",
}


def load_deliveries(csv_path: str | Path) -> pd.DataFrame:
    """Load ball-by-ball deliveries data from CSV."""
    df = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    return df


def batting_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return batter-level summary sorted by runs scored."""
    summary = (
        df.groupby("striker", as_index=False)
        .agg(
            runs=("runs_off_bat", "sum"),
            balls=("runs_off_bat", "count"),
            fours=("runs_off_bat", lambda s: (s == 4).sum()),
            sixes=("runs_off_bat", lambda s: (s == 6).sum()),
        )
        .assign(strike_rate=lambda d: (d["runs"] / d["balls"] * 100).round(2))
        .sort_values("runs", ascending=False)
    )
    return summary


def bowling_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return bowler-level summary sorted by wickets taken."""
    summary = (
        df.groupby("bowler", as_index=False)
        .agg(
            balls=("bowler", "count"),
            runs_conceded=("runs_off_bat", "sum"),
            extras=("extras", "sum"),
            wickets=("wicket_type", lambda s: s.fillna("").ne("").sum()),
        )
        .assign(
            overs=lambda d: (d["balls"] // 6).astype(str)
            + "."
            + (d["balls"] % 6).astype(str),
            economy=lambda d: ((d["runs_conceded"] + d["extras"]) / (d["balls"] / 6)).round(2),
            strike_rate=lambda d: (
                d["balls"].where(d["wickets"] > 0) / d["wickets"].where(d["wickets"] > 0)
            ).round(2),
        )
        .sort_values(["wickets", "economy"], ascending=[False, True])
    )
    return summary


def team_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Return match-level team totals."""
    totals = (
        df.assign(total_runs=lambda d: d["runs_off_bat"] + d["extras"])
        .groupby(["match_id", "innings", "batting_team"], as_index=False)["total_runs"]
        .sum()
        .sort_values(["match_id", "innings"])
    )
    return totals


def run_analysis(input_csv: str | Path, output_dir: str | Path) -> None:
    """Execute the analysis pipeline and persist outputs."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    deliveries = load_deliveries(input_csv)

    batting = batting_summary(deliveries)
    bowling = bowling_summary(deliveries)
    totals = team_totals(deliveries)

    batting.to_csv(output_dir / "batting_summary.csv", index=False)
    bowling.to_csv(output_dir / "bowling_summary.csv", index=False)
    totals.to_csv(output_dir / "team_totals.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a cricket match analysis pipeline")
    parser.add_argument(
        "--input",
        default="data/sample_deliveries.csv",
        help="Path to ball-by-ball deliveries CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where analysis CSV files will be written",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_analysis(args.input, args.output_dir)
