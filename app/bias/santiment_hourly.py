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


class SantimentHourlyBias(BiasInterface):
    paid = True

    def __init__(self):
        self.api_key = os.getenv("SANTIMENT_API_KEY", "")
        self.metrics = {
            "hour": "sentiment_weighted_total_1h",
            "reddit": "sentiment_weighted_reddit_1h",
            "twitter": "sentiment_weighted_twitter_1h",
        }

    @cache
    def get_slug(self, ticker: str) -> str:
        for asset in SANTIMENT_ASSETS["data"]["allProjects"]:
            if asset["ticker"].lower() == ticker.lower():
                return asset["slug"]
        logger.warning(f"Ticker '{ticker}' not found in Santiment assets.")
        return "bitcoin"

    def iso_date(self, hours_ago: int = 0) -> str:
        dt = datetime.utcnow() - timedelta(hours=hours_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def fetch_sentiment_data(self, symbol: str, metric: str, hours: int, offset_hours: int) -> list[float]:
        headers = {
            "Content-Type": "application/graphql",
            "Authorization": f"Apikey {self.api_key}",
        }

        to_time = self.iso_date(offset_hours)
        from_time = self.iso_date(offset_hours + hours)

        query = f"""
        {{
            getMetric(metric: "{metric}") {{
                timeseriesData(
                    slug: "{self.get_slug(symbol)}",
                    from: "{from_time}",
                    to: "{to_time}",
                    interval: "1h"
                ) {{
                    datetime
                    value
                }}
            }}
        }}
        """
        print(query)

        try:
            logger.info(f"Fetching '{metric}' data for '{symbol}' from {from_time} to {to_time}")
            response = requests.post(
                "https://api.santiment.net/graphql",
                headers=headers,
                data=query,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response data: {json.dumps(data, indent=2)}")

            if data.get("errors"):
                logger.error(f"Santiment API error: {data['errors']}")
                raise Exception(data["errors"][0].get("message", "Unknown error"))

            points = data["data"]["getMetric"]["timeseriesData"]
            values = [p["value"] for p in points if p["value"] is not None]
            return values[-3:]  # Just in case more than needed

        except Exception as e:
            logger.exception(f"Failed to fetch metric {metric}: {e}")
            return []

    def average(self, vals):
        return sum(vals) / len(vals) if vals else 0.0

    def compute_smart_metric(self, values: list[float]) -> float:
        """Compute a smarter metric than just average: weighted momentum."""
        if not values:
            return 0.0
        # Give higher weight to recent values
        weights = [i + 1 for i in range(len(values))]  # [1, 2, ..., n]
        weighted = [v * w for v, w in zip(values, weights)]
        return sum(weighted) / sum(weights)

    def classify(self, score: float) -> BiasType:
        threshold = float(get_config("SantimentThreshold", 0.25))
        if score > threshold:
            return BiasType.LONG
        elif score < -threshold:
            return BiasType.SHORT
        else:
            return BiasType.NEUTRAL

    def bias(self, biasRequest: BiasRequest) -> BiasResponse:
        symbol = biasRequest.symbol
        offset_days = int(get_config("SantimentHourlyDaysAgo", 0))
        lookback_hours = int(get_config("SantimentHourlyHoursToLookBack", 3))
        offset_hours = offset_days * 24

        main_vals = self.fetch_sentiment_data(symbol, self.metrics["hour"], lookback_hours, offset_hours)
        reddit_vals = self.fetch_sentiment_data(symbol, self.metrics["reddit"], lookback_hours, offset_hours)
        twitter_vals = self.fetch_sentiment_data(symbol, self.metrics["twitter"], lookback_hours, offset_hours)

        if len(main_vals) < 3:
            return BiasResponse(
                bias=BiasType.NEUTRAL,
                usedSymbol=True,
                error="Not enough main sentiment data",
                reason="Santiment did not return enough data"
            )

        def sign(x): return 1 if x > 0 else -1 if x < 0 else 0

        main_score = self.compute_smart_metric(main_vals)
        reddit_score = self.compute_smart_metric(reddit_vals)
        twitter_score = self.compute_smart_metric(twitter_vals)

        main_sign = sign(main_score)
        reddit_sign = sign(reddit_score)
        twitter_sign = sign(twitter_score)

        agreement = sum([
            reddit_sign == main_sign and reddit_sign != 0,
            twitter_sign == main_sign and twitter_sign != 0
        ])
        confidence = ["low", "medium", "high"][agreement]

        if agreement == 2:
            trust_score = main_score
        elif agreement == 1:
            trust_score = main_score * 0.7
        else:
            trust_score = main_score * 0.4

        classification = self.classify(trust_score)

        logger.info(f"Main metric: {main_score:.4f}, Reddit: {reddit_score:.4f}, Twitter: {twitter_score:.4f}")
        logger.info(f"Agreement: {agreement}/2 → Confidence: {confidence}")
        logger.info(f"Trust score: {trust_score:.4f} → Final Bias: {classification}")

        return BiasResponse(
            bias=classification,
            usedSymbol=True,
            reason=f"Computed trust score {trust_score:.4f} with {confidence} confidence and {agreement}/2 validation."
        )
