"""
FXCompare

Main application.

Usage:
    python3 app.py
        Show today's effective rates and the best option without converting
        a specific amount.

    python3 app.py 200
        Compare the MXN value of USD 200 and indicate whether CAMNOSA or a
        card offers better value after the configured bank fee.

The comparison answers: "Is it better today to exchange USD for MXN at
CAMNOSA, or pay in MXN with a USD card?"
"""

import argparse

from fxcompare.chart import CHART_PATH, generate_history_chart
from fxcompare.compare import compare_rates, effective_rate
from fxcompare.config import load_config
from fxcompare.history import HISTORY_PATH, update_daily_history
from fxcompare.providers import camnosa, mastercard, visa


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare the MXN cost of buying or spending USD."
    )
    parser.add_argument(
        "amount",
        nargs="?",
        type=float,
        help="optional amount in USD to buy or spend",
    )
    args = parser.parse_args()

    if args.amount is not None and args.amount <= 0:
        parser.error("amount must be greater than zero")

    return args


def main():
    args = parse_args()
    config = load_config()
    foreign_fee_percent = float(config["foreign_fee_percent"])

    rates = [
        camnosa.get_rate(),
        visa.get_rate(),
        mastercard.get_rate(),
    ]

    best = compare_rates(rates, foreign_fee_percent)
    history_changed = update_daily_history(
        rates,
        foreign_fee_percent,
        best.provider,
    )
    chart_changed = history_changed or not CHART_PATH.exists()
    if chart_changed:
        generate_history_chart(HISTORY_PATH)

    print()
    print("=" * 40)
    print(" FXCompare")
    print("=" * 40)
    print()

    for rate in rates:
        rate_with_fee = effective_rate(rate, foreign_fee_percent)
        rate_details = (
            f"{rate.provider:12} "
            f"Base: MXN {rate.buy:,.4f}   "
            f"Efectiva: MXN {rate_with_fee:,.4f} por USD"
        )

        if args.amount is None:
            print(rate_details)
        else:
            total = rate_with_fee * args.amount
            print(f"{rate_details}   Valor: MXN {total:,.2f}")

    print()
    if args.amount is None:
        print(f"Mejor tasa efectiva: {best.provider}")
    else:
        best_total = effective_rate(best, foreign_fee_percent) * args.amount
        print(f"Mejor opción para USD {args.amount:,.2f}: {best.provider}")
        print(f"Valor estimado: MXN {best_total:,.2f}")

    print(f"Comisión bancaria para tarjetas: {foreign_fee_percent:g}%")
    history_status = "actualizado" if history_changed else "sin cambios"
    print(f"Historial diario: {history_status} ({HISTORY_PATH})")
    chart_status = "actualizado" if chart_changed else "sin cambios"
    print(f"Gráfico histórico: {chart_status} ({CHART_PATH})")
    print()


if __name__ == "__main__":
    main()
