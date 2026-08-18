"""Generate a line chart from the daily exchange-rate history."""

import csv
import os
from datetime import date, timedelta
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent.parent / ".cache" / "matplotlib"
CACHE_PATH.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(CACHE_PATH))
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_PATH.parent))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


CHART_PATH = Path(__file__).resolve().parent.parent / "history" / "rates.png"
SERIES = (
    ("CAMNOSA", "camnosa_effective_latest"),
    ("VISA", "visa_effective_latest"),
    ("MASTERCARD", "mastercard_effective_latest"),
)


def generate_history_chart(history_path: Path, chart_path: Path = CHART_PATH) -> None:
    """Create a PNG line chart using each day's latest effective rates."""
    with history_path.open(newline="", encoding="utf-8") as history_file:
        rows = list(csv.DictReader(history_file))

    if not rows:
        return

    dates = [date.fromisoformat(row["date"]) for row in rows]
    figure, axis = plt.subplots(figsize=(10, 5.5))

    for label, column in SERIES:
        values = [float(row[column]) for row in rows]
        axis.plot(dates, values, marker="o", linewidth=2, label=label)
        axis.annotate(
            f"{values[-1]:.4f}",
            (dates[-1], values[-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
        )

    if len(dates) == 1:
        axis.set_xlim(dates[0] - timedelta(days=1), dates[0] + timedelta(days=1))

    span_days = max((max(dates) - min(dates)).days, 1)
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, span_days // 7)))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axis.set_title("Tasa efectiva diaria: efectivo vs. tarjeta")
    axis.set_xlabel("Fecha")
    axis.set_ylabel("MXN de valor por USD")
    axis.grid(True, alpha=0.25)
    axis.legend()
    figure.autofmt_xdate()
    figure.tight_layout()

    chart_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = chart_path.with_suffix(".tmp")
    figure.savefig(temporary_path, format="png", dpi=160)
    plt.close(figure)
    temporary_path.replace(chart_path)
