import requests


def rub_to_btc(rub: int) -> float:
    response = requests.get("https://blockchain.info/tobtc", params={"currency": "RUB", "value": rub})
    return float(response.text)
