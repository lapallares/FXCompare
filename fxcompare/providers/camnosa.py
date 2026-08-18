"""
CAMNOSA exchange rate provider.
"""

from datetime import datetime

from fxcompare.models import ExchangeRate
from fxcompare.providers.client import session

URL = "https://camnosa.com/api/tipo-de-cambio/"


def get_rate() -> ExchangeRate:
    """
    Retrieve the current USD exchange rate from CAMNOSA.
    """

    response = session().get(URL, timeout=10)
    response.raise_for_status()

    data = response.json()

    return ExchangeRate(
        provider="CAMNOSA",
        currency_pair="USD/MXN",
        buy=float(data["usd"]["compra"]),
        sell=float(data["usd"]["venta"]),
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    print(get_rate())
