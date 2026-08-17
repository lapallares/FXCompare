"""
Common data models used by FXCompare.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ExchangeRate:
    """
    Represents an exchange rate returned by any provider.
    """

    provider: str
    currency_pair: str
    buy: float
    sell: float | None
    timestamp: datetime