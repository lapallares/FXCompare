"""
Comparison utilities.
"""

from fxcompare.models import ExchangeRate


def effective_rate(rate: ExchangeRate, foreign_fee_percent: float) -> float:
    """
    Return the effective MXN value of one USD for a provider.

    CAMNOSA buys the customer's USD, so its buy rate applies. For card
    networks, the bank's foreign transaction fee reduces the spending value.
    """
    if rate.provider == "CAMNOSA":
        return rate.buy

    return rate.buy / (1 + foreign_fee_percent / 100)


def compare_rates(
    rates: list[ExchangeRate], foreign_fee_percent: float = 0
) -> ExchangeRate:
    """Return the provider with the highest effective MXN value per USD."""
    return max(rates, key=lambda rate: effective_rate(rate, foreign_fee_percent))
