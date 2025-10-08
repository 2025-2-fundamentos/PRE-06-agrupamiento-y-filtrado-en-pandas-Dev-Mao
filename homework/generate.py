from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_inputs(base_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    input_dir = base_dir / "files" / "input"
    drivers = pd.read_csv(input_dir / "drivers.csv")
    timesheet = pd.read_csv(input_dir / "timesheet.csv")
    return drivers, timesheet


def build_summary(drivers: pd.DataFrame, timesheet: pd.DataFrame) -> pd.DataFrame:
    totals = (
        timesheet
        .groupby("driverId", as_index=False)[["hours-logged", "miles-logged"]]
        .sum()
        .rename(columns={
            "hours-logged": "total_hours",
            "miles-logged": "total_miles",
        })
    )

    summary = drivers[["driverId", "name"]].merge(totals, on="driverId", how="left")
    summary["total_hours"] = summary["total_hours"].fillna(0).astype(int)
    summary["total_miles"] = summary["total_miles"].fillna(0).astype(int)
    return summary.sort_values(["total_miles", "total_hours"], ascending=False)


def save_summary(summary: pd.DataFrame, base_dir: Path) -> Path:
    out_dir = base_dir / "files" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.csv"
    summary.to_csv(out_path, index=False)
    return out_path


def save_top10_plot(summary: pd.DataFrame, base_dir: Path) -> Path:
    plots_dir = base_dir / "files" / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plots_dir / "top10_drivers.png"

    top10 = summary.nlargest(10, "total_miles")
    plt.figure(figsize=(10, 6))
    plt.barh(top10["name"], top10["total_miles"], color="#4C78A8")
    plt.gca().invert_yaxis()
    plt.xlabel("Total miles")
    plt.title("Top 10 drivers by miles")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    return plot_path


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    drivers, timesheet = load_inputs(base_dir)
    summary = build_summary(drivers, timesheet)
    save_summary(summary, base_dir)
    save_top10_plot(summary, base_dir)


if __name__ == "__main__":
    main()


