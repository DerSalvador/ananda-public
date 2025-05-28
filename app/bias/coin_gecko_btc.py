from functools import cache
import os

import requests
from bias import BiasInterface, BiasRequest, BiasResponse, BiasType
from bias.constants import COIN_GECKO_SYMBOLS
from utils import get_logger

logger = get_logger()


class CoinGeckoBTC(BiasInterface):
    paid = True
    def get_bitcoin_data(self, biasRequest: BiasRequest):
        API_URL = "https://pro-api.coingecko.com/api/v3"
        COINGECKO_API_KEY=os.getenv("COINGECKO_API_KEY", "")
        endpoint = f"{API_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": self.getidfromsymbol(biasRequest.symbol),
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
            "x_cg_pro_api_key": COINGECKO_API_KEY,
        }
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data[0] if data else None

    def analyze_trend_day(self, bitcoin_data):
        change_24h = bitcoin_data.get("price_change_percentage_24h", 0)
        # change_7d = bitcoin_data.get("price_change_percentage_7d_in_currency", 0)
        volume = bitcoin_data.get("total_volume", 0)

        # Determine bias based on 24-hour and 7-day changes
        if change_24h > 0: # and change_7d > 0:
            trend = BiasType.LONG
            reason = f"Price change 24h: {change_24h:.2f}% positive"
        elif change_24h < 0: # and change_7d < 0:
            trend = BiasType.SHORT
            reason = f"Price change 24h: {change_24h:.2f}% negative"
        else:
            trend = BiasType.NEUTRAL
            reason = "No significant change in price"

        return trend, reason


    def bias(self, biasRequest: BiasRequest) -> BiasResponse:
        bitcoin_data = self.get_bitcoin_data(biasRequest)
        trend_bias, reason = self.analyze_trend_day(bitcoin_data)
        return BiasResponse(bias=trend_bias, reason=reason, usedSymbol=True)

    @cache
    def getidfromsymbol(self, symbol):
        """
        Get the CoinGecko ID from the symbol.
        """
        for coin in COIN_GECKO_SYMBOLS:
            if coin["symbol"].lower() == symbol.lower():
                return coin["id"]
        logger.warning(f"Symbol {symbol} not found in COIN_GECKO_SYMBOLS.")
        return "bitcoin"


