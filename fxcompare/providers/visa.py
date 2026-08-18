"""
Visa exchange rate provider.
"""

from datetime import date

from fxcompare.models import ExchangeRate
from fxcompare.providers.client import session
from fxcompare.providers.utils import get_json, to_float


URL = "https://www.visa.co.in/cmsapi/fx/rates"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.visa.co.in/support/consumer/travel-support/exchange-rate-calculator.html",
}


def get_rate(
    home="MXN",
    spend="USD",
    amount=1000,
) -> ExchangeRate:

    today = date.today()
    mdy = today.strftime("%m/%d/%Y")

    data = get_json(
        session(),
        URL,
        HEADERS,
        {
            "amount": str(amount),
            "fee": "0",
            "utcConvertedDate": mdy,
            "exchangedate": mdy,
            "fromCurr": home,
            "toCurr": spend,
        },
    )

    if not data:
        raise RuntimeError("Visa request failed")

    if data.get("status") != "success":
        raise RuntimeError("Visa returned an error")

    values = data["originalValues"]

    return ExchangeRate(
        provider="VISA",
        currency_pair="USD/MXN",
        buy=to_float(values["fxRateVisa"]),
        sell=None,
        timestamp=today,
    )


if __name__ == "__main__":
    print(get_rate())
