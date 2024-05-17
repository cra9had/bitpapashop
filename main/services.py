import requests
from django.conf import settings
from decimal import *


def rub_to_btc(rub: int) -> Decimal:
    response = requests.get("https://bitpapa.com/api/v1/exchange_rates/all", headers={
        "Accept": "application/json",
        "X-Access-Token": settings.BITPAPA_API_KEY,
    })
    return round(Decimal(rub) / Decimal(response.json()["rates"]["BTC_RUB"]), 8)
