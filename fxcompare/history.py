"""Daily exchange-rate history stored as a CSV table."""

import csv
from datetime import datetime
from pathlib import Path

from fxcompare.compare import effective_rate
from fxcompare.models import ExchangeRate


HISTORY_PATH = Path(__file__).resolve().parent.parent / "history" / "history.csv"
PROVIDERS = ("CAMNOSA", "VISA", "MASTERCARD")

FIELDNAMES = [
    "date",
    "first_changed_at",
    "last_changed_at",
    "changes",
    "foreign_fee_percent",
]
for provider in PROVIDERS:
    prefix = provider.lower()
    for rate_kind in ("base", "effective"):
        for statistic in ("first", "latest", "min", "max"):
            FIELDNAMES.append(f"{prefix}_{rate_kind}_{statistic}")
FIELDNAMES.extend(("best_first", "best_latest"))


def _format_rate(value: float) -> str:
    return f"{value:.6f}"


def _current_values(
    rates: list[ExchangeRate], foreign_fee_percent: float
) -> dict[str, tuple[float, float]]:
    return {
        rate.provider: (
            rate.buy,
            effective_rate(rate, foreign_fee_percent),
        )
        for rate in rates
    }


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open(newline="", encoding="utf-8") as history_file:
        return list(csv.DictReader(history_file))


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open("w", newline="", encoding="utf-8") as history_file:
        writer = csv.DictWriter(
            history_file,
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    temporary_path.replace(path)


def update_daily_history(
    rates: list[ExchangeRate],
    foreign_fee_percent: float,
    best_provider: str,
    path: Path = HISTORY_PATH,
) -> bool:
    """Insert today's row or update it only when a recorded value changed."""
    now = datetime.now().astimezone()
    day = now.date().isoformat()
    changed_at = now.isoformat(timespec="seconds")
    current = _current_values(rates, foreign_fee_percent)
    rows = _read_rows(path)
    row = next((item for item in rows if item["date"] == day), None)

    if row is None:
        row = {
            "date": day,
            "first_changed_at": changed_at,
            "last_changed_at": changed_at,
            "changes": "1",
            "foreign_fee_percent": _format_rate(foreign_fee_percent),
            "best_first": best_provider,
            "best_latest": best_provider,
        }
        for provider, (base, effective) in current.items():
            prefix = provider.lower()
            for rate_kind, value in (("base", base), ("effective", effective)):
                formatted = _format_rate(value)
                for statistic in ("first", "latest", "min", "max"):
                    row[f"{prefix}_{rate_kind}_{statistic}"] = formatted
        rows.append(row)
        _write_rows(path, rows)
        return True

    rates_unchanged = all(
        row[f"{provider.lower()}_base_latest"] == _format_rate(base)
        and row[f"{provider.lower()}_effective_latest"] == _format_rate(effective)
        for provider, (base, effective) in current.items()
    )
    fee_unchanged = row["foreign_fee_percent"] == _format_rate(
        foreign_fee_percent
    )
    if rates_unchanged and fee_unchanged and row["best_latest"] == best_provider:
        return False

    row["last_changed_at"] = changed_at
    row["changes"] = str(int(row["changes"]) + 1)
    row["foreign_fee_percent"] = _format_rate(foreign_fee_percent)
    row["best_latest"] = best_provider

    for provider, (base, effective) in current.items():
        prefix = provider.lower()
        for rate_kind, value in (("base", base), ("effective", effective)):
            row[f"{prefix}_{rate_kind}_latest"] = _format_rate(value)
            minimum_key = f"{prefix}_{rate_kind}_min"
            maximum_key = f"{prefix}_{rate_kind}_max"
            row[minimum_key] = _format_rate(min(float(row[minimum_key]), value))
            row[maximum_key] = _format_rate(max(float(row[maximum_key]), value))

    _write_rows(path, rows)
    return True
