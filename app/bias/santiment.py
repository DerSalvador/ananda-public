from functools import cache
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional
from bias import get_config
from bias.constants import SANTIMENT_ASSETS
from utils import get_logger
from bias import BiasInterface, BiasRequest, BiasResponse, BiasType

logger = get_logger()


class SantimentBias(BiasInterface):
    paid = True

    def __init__(self):
        self.api_key = os.getenv("SANTIMENT_API_KEY", "")
        self.metric = "sentiment_weighted_total_1d_v2"

    @cache
    def get_slug(self, ticker: str) -> str:
        for asset in SANTIMENT_ASSETS["data"]["allProjects"]:
            if asset["ticker"].lower() == ticker.lower():
                return asset["slug"]
        logger.warning(f"Ticker '{ticker}' not found in Santiment assets.")
        return "bitcoin"

    def iso_date(self, days_ago: int = 0) -> str:
        dt = datetime.utcnow() - timedelta(days=days_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def fetch_sentiment_data(self, symbol: str) -> Optional[list[float]]:
        headers = {
            "Content-Type": "application/graphql",
            "Authorization": f"Apikey {self.api_key}",
        }

        SantimentFromTimeDaysAgo = int(get_config("SantimentFromTimeDaysAgo", 7))
        SantimentToTimeDaysAgo = int(get_config("SantimentToTimeDaysAgo", 0))
        from_time = self.iso_date(SantimentFromTimeDaysAgo)
        to_time = self.iso_date(SantimentToTimeDaysAgo)

        query = f"""
        {{
            getMetric(metric: "{self.metric}") {{
                timeseriesData(
                    slug: "{self.get_slug(symbol)}",
                    from: "{from_time}",
                    to: "{to_time}",
                    interval: "1d"
                ) {{
                    datetime
                    value
                }}
            }}
        }}
        """

        try:
            logger.info(f"Requesting sentiment data for '{symbol}' from {from_time} to {to_time}")
            response = requests.post(
                "https://api.santiment.net/graphql",
                headers=headers,
                data=query,
                timeout=10
            )
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            logger.debug(data)
            if data.get("errors"):
                logger.error(f"Santiment API error: {data['errors']}")
                error_message = data["errors"][0].get("message", "Unknown error")
                raise Exception(error_message)

            points = data["data"]["getMetric"]["timeseriesData"]
            values = [point["value"] for point in points if point["value"] is not None]

            logger.info(f"Fetched {len(values)} sentiment values")
            return values[-6:]  # Last 6: previous 5 + latest
        except Exception as e:
            logger.exception(f"Error fetching data from Santiment: {e}")
            raise e

    def bias(self, biasRequest: BiasRequest) -> BiasResponse:
        values = self.fetch_sentiment_data(biasRequest.symbol)


        if values is None or len(values) < 6:
            return BiasResponse(
                bias=BiasType.NEUTRAL,
                error="Not enough data to determine signal.",
                usedSymbol=True,
                reason="Santiment API returned insufficient or invalid data."
            )

        *prev5, latest = values[-6:]  # Unpack last 6 into prev5 and latest
        average = sum(prev5) / len(prev5)
        diff = latest - average
        threshold = float(get_config("SantimentThreshold", 0.25))

        logger.info(f"Latest sentiment: {latest:.2f}")
        logger.info(f"Previous 5-day average: {average:.2f}")
        logger.info(f"Difference: {diff:.4f} | Threshold: ±{threshold}")

        if diff > threshold:
            signal = BiasType.LONG
            reason = f"Signal: LONG — Diff {diff:.4f} > Threshold {threshold}"
        elif diff < -threshold:
            signal = BiasType.SHORT
            reason = f"Signal: SHORT — Diff {diff:.4f} < -Threshold {-threshold}"
        else:
            signal = BiasType.NEUTRAL
            reason = f"Signal: HOLD — Diff {diff:.4f} within ±{threshold}"

        return BiasResponse(
            bias=signal,
            usedSymbol=True,
            reason=reason
        )

