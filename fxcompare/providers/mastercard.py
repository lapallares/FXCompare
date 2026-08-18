"""
Mastercard exchange rate provider.
"""

from datetime import date

from fxcompare.models import ExchangeRate
from fxcompare.providers.client import session


URL = (
    "https://www.mastercard.com/"
    "marketingservices/public/mccom-services/"
    "currency-conversions/conversion-rates"
)


def get_rate() -> ExchangeRate:
    response = session().get(
        URL,
        params={
            "exchange_date": date.today().strftime("%Y-%m-%d"),
            "transaction_currency": "MXN",
            "cardholder_billing_currency": "USD",
            "bank_fee": "0",
            "transaction_amount": "1000",
        },
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()["data"]

    # API devuelve USD por MXN
    usd_per_mxn = float(data["conversionRate"])

    # nosotros queremos MXN por USD
    mxn_per_usd = 1 / usd_per_mxn

    return ExchangeRate(
        provider="MASTERCARD",
        currency_pair="USD/MXN",
        buy=mxn_per_usd,
        sell=None,
        timestamp=date.today(),
    )


if __name__ == "__main__":
    print(get_rate())
