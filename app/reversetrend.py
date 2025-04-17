import json
import os
import requests

from utils import TimeBasedDeque, get_logger


profit_queue = {}

def cron_update_profit():
    logger = get_logger()
    status_endpoint = "/api/v1/status"
    logger.info("Fetching status from Freqtrade API")
    FREQTRADE_BASE_URL = os.getenv("FREQTRADE_BASE_URL", "")
    if not FREQTRADE_BASE_URL:
        logger.error("FREQTRADE_BASE_URL is not set")
        return
    url = f"{FREQTRADE_BASE_URL}{status_endpoint}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()
    for item in data:
        pair = item["pair"]
        symbol = pair.split("/")[0]
        profit = item.get("profit_pct")
        is_short = item.get("is_short", False)
        if not profit:
            continue
        if symbol not in profit_queue:
            profit_queue[symbol] = TimeBasedDeque()
        queue_item = {
            "symbol": symbol,
            "profit": profit,
            "is_short": is_short
        }
        profit_queue[symbol].add(queue_item)
        logger.info(f"Updated profit for {symbol}: {profit}")
    return data

def get_profits(symbol: str):
    if symbol not in profit_queue:
        return []
    items_and_times = profit_queue[symbol].get_items_and_times()
    for i in range(len(items_and_times)):
        items_and_times[i] = {
            "timestamp": items_and_times[i][0],
            "profit": items_and_times[i][1]["profit"],
            "is_short": items_and_times[i][1]["is_short"]
        }
    return items_and_times
