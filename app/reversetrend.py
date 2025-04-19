import json
import os
import requests
import pandas as pd

from bias import get_config, update_config
from utils import TimeBasedDeque, get_logger

logger = get_logger()

profit_queue = {}

def cron_update_profit():
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

def has_min_count(profits, symbol: str):
    min_length = int(get_config("ReverseTrendCheckMinCount", 60))
    if len(profits) < min_length:
        return f"Insufficient data {len(profits)} for {symbol} to check reverse trend", False
    return f"{len(profits)} > {min_length}", True

def negative_percent(profits, symbol: str):
    reverse_trend_negative_percent = float(get_config("ReverseTrendShouldBeNegativePercent", 100))
    negative_count = sum(1 for profit in profits if profit.get("profit", 0) < 0)
    total_count = len(profits)
    negative_percent = (negative_count / total_count) * 100
    if negative_percent >= reverse_trend_negative_percent:
        return f"{negative_percent:.2f}% >= {reverse_trend_negative_percent}% for {symbol}", True
    return f"{negative_percent:.2f}% < {reverse_trend_negative_percent} for {symbol}", False

def first_greater_than_last(profits, symbol: str):
    check_first_greater_than_last = get_config("ReverseTrendCheckFirstGreater", "true") == "true"
    if not check_first_greater_than_last:
        return f"Check first greater than last is disabled for {symbol}", True

    if not profits:
        return f"No profits data for {symbol}", False

    first_profit = profits[0].get("profit", 0)
    last_profit = profits[-1].get("profit", 0)
    if first_profit >= last_profit:
        return f"First profit {first_profit} >= last profit {last_profit} for {symbol}", True
    return f"First profit {first_profit} < last profit {last_profit} for {symbol}", False

class Trend:
    LINEAR_STABLE = "Linear Stable"
    BULLISH = "Bullish"
    BEARISH = "Bearish"

def populateTrend(df: pd.DataFrame) -> pd.DataFrame:
    short_window = int(get_config("ReverseTrendMACDShortWindow", 6))
    long_window = int(get_config("ReverseTrendMACDLongWindow", 26))
    signal_window = int(get_config("ReverseTrendMACDSignalWindow", 9))

    df['EMA_short'] = df['current_profit'].ewm(span=short_window, adjust=True).mean()
    df['EMA_long'] = df['current_profit'].ewm(span=long_window, adjust=True).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['Trend'] = df.apply(lambda row: 'Bullish' if row['MACD'] > row['Signal_Line'] else 'Bearish', axis=1)

    return df

def determineTrend(overall_result, partial_length, df, label: str):
    bullish_count = df['Trend'].value_counts().get('Bullish', 0)
    bearish_count = df['Trend'].value_counts().get('Bearish', 0)

    bullish_threshold = float(get_config("ReverseTrendBullishPartialThresholdPct", 0.7))
    bearish_threshold = float(get_config("ReverseTrendBearishPartialThresholdPct", 0.7))

    if bullish_count / partial_length >= bullish_threshold or overall_result == Trend.BULLISH:
        return Trend.BULLISH, f"{label}: Bullish {bullish_count}/{partial_length} ≥ {bullish_threshold}"
    elif bearish_count / partial_length >= bearish_threshold or overall_result == Trend.BEARISH:
        return Trend.BEARISH, f"{label}: Bearish {bearish_count}/{partial_length} ≥ {bearish_threshold}"
    else:
        return Trend.LINEAR_STABLE, f"{label}: No clear trend (Bullish {bullish_count}/{partial_length}, Bearish {bearish_count}/{partial_length})"

def detectBullishOrBearishCandle(df: pd.DataFrame):
    if df.empty:
        return "Dataframe empty → Linear Stable", Trend.LINEAR_STABLE

    df = populateTrend(df)

    bullish_threshold = float(get_config("ReverseTrendBullishThresholdPct", 0.7))
    bearish_threshold = float(get_config("ReverseTrendBearishThresholdPct", 0.7))

    bullish_count = df['Trend'].value_counts().get('Bullish', 0)
    bearish_count = df['Trend'].value_counts().get('Bearish', 0)
    total = len(df)

    if bullish_count / total >= bullish_threshold:
        overall_result = Trend.BULLISH
        reason = f"Overall: Bullish {bullish_count}/{total} ≥ {bullish_threshold}"
    elif bearish_count / total >= bearish_threshold:
        overall_result = Trend.BEARISH
        reason = f"Overall: Bearish {bearish_count}/{total} ≥ {bearish_threshold}"
    else:
        overall_result = Trend.LINEAR_STABLE
        reason = f"Overall: No clear trend (Bullish {bullish_count}/{total}, Bearish {bearish_count}/{total})"

    candle_divisor = float(get_config("ReverseTrendCandleDivisor", 3.0))
    partial_length = round(float(total) // candle_divisor)

    if partial_length > 0 and total > partial_length:
        last_partial_df = df[-partial_length:]
        first_partial_df = df[:-partial_length]

        first_trend, first_reason = determineTrend(overall_result, partial_length, first_partial_df, "First")
        last_trend, last_reason = determineTrend(overall_result, partial_length, last_partial_df, "Last")

        last_entries = int(get_config("ReverseTrendLastTrendEntries", 3))
        last_entries = min(last_entries, total)
        last_trends = df['Trend'].tail(last_entries)

        all_bullish = all(last_trends == 'Bullish')
        all_bearish = all(last_trends == 'Bearish')

        if all_bullish and overall_result == Trend.BULLISH and first_trend == Trend.BULLISH and last_trend == Trend.BULLISH:
            return "All segments bullish → Bullish trend confirmed", Trend.BULLISH
        elif all_bearish and overall_result == Trend.BEARISH and first_trend == Trend.BEARISH and last_trend == Trend.BEARISH:
            return "All segments bearish → Bearish trend confirmed", Trend.BEARISH
        else:
            return f"Segments mixed → {reason}", Trend.LINEAR_STABLE
    else:
        return f"{reason} (not enough data for partial analysis)", Trend.LINEAR_STABLE

def is_linear_decreasing(profits, symbol: str):
    if get_config("ReverseTrendCheckLinearDecreasing", "true") != "true":
        return f"Linear decreasing check disabled for {symbol}", True

    df = pd.DataFrame([p.get("profit", 0) for p in profits], columns=["current_profit"])
    reason, trend = detectBullishOrBearishCandle(df)

    if trend == Trend.BEARISH:
        return f"{symbol}: {reason}", True
    else:
        return f"{symbol}: {reason}", False

def reverse_trend(symbol: str, full=False):
    profits = get_profits(symbol)
    response = {}
    response["final"] = {
        "value": False,
        "is_short": profits[-1]["is_short"] if profits else False,
        "reason": ""
    }

    # Minimum count
    has_min_count_reason, has_min_count_bool = has_min_count(profits, symbol)
    response["min_count"] = {
        "reason": has_min_count_reason,
        "value": has_min_count_bool
    }
    if not has_min_count_bool:
        response["final"]["reason"] = has_min_count_reason
        if not full:
            return response

    # All Negative (or percentage negative)
    negative_percent_reason, negative_percent_bool = negative_percent(profits, symbol)
    response["negative_percent"] = {
        "reason": negative_percent_reason,
        "value": negative_percent_bool
    }
    if not negative_percent_bool:
        response["final"]["reason"] = negative_percent_reason
        if not full:
            return response

    # First greater than last
    first_greater_than_last_reason, first_greater_than_last_bool = first_greater_than_last(profits, symbol)
    response["first_greater_than_last"] = {
        "reason": first_greater_than_last_reason,
        "value": first_greater_than_last_bool
    }
    if not first_greater_than_last_bool:
        response["final"]["reason"] = first_greater_than_last_reason
        if not full:
            return response

    # Linear decreasing
    linear_decreasing_reason, linear_decreasing_bool = is_linear_decreasing(profits, symbol)
    response["linear_decreasing"] = {
        "reason": linear_decreasing_reason,
        "value": linear_decreasing_bool
    }
    if not linear_decreasing_bool:
        response["final"]["reason"] = linear_decreasing_reason
        if not full:
            return response

    # Final result
    if response["min_count"]["value"] and response["negative_percent"]["value"] and response["first_greater_than_last"]["value"] and response["linear_decreasing"]["value"]:
        response["final"]["value"] = True
        response["final"]["reason"] = "All checks passed"
    else:
        response["final"]["reason"] = "One or more checks failed"
    return response

def get_profits(symbol: str):
    if symbol not in profit_queue:
        return []
    config_seconds = int(get_config("ReverseTrendCheckBackSeconds", 60*10))
    items_and_times = profit_queue[symbol].get_items_and_times_last_x_seconds(config_seconds)
    for i in range(len(items_and_times)):
        items_and_times[i] = {
            "timestamp": items_and_times[i][0],
            "profit": items_and_times[i][1]["profit"],
            "is_short": items_and_times[i][1]["is_short"]
        }
    return items_and_times
