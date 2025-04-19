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
    short_window=int(get_config("ReverseTrendMACDShortWindow", 6))
    long_window=int(get_config("ReverseTrendMACDLongWindow", 26))
    signal_window=int(get_config("ReverseTrendMACDSignalWindow", 9))
    # Calculate the short term exponential moving average (EMA)
    df['EMA_short'] = df['current_profit'].ewm(span=short_window, adjust=True).mean()
    # Calculate the long term exponential moving average (EMA)
    df['EMA_long'] = df['current_profit'].ewm(span=long_window, adjust=True).mean()
    # Calculate the MACD line
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    # Calculate the Signal line
    df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    # Determine the trend
    df['Trend'] = df.apply(lambda row: 'Bullish' if row['MACD'] > row['Signal_Line'] else 'Bearish', axis=1)
    return df

def determineTrend(overall_result, partial_length, df):
    bullish_count = df['Trend'].value_counts().get('Bullish', 0)
    bearish_count = df['Trend'].value_counts().get('Bearish', 0)
    bullish_partial_threshold_pct = float(get_config("ReverseTrendBullishPartialThresholdPct", 0.7))
    bearish_partial_threshold_pct = float(get_config("ReverseTrendBearishPartialThresholdPct", 0.7))
    if bullish_count / partial_length >= bullish_partial_threshold_pct or overall_result == Trend.BULLISH:
        return Trend.BULLISH
    elif bearish_count / partial_length >= bearish_partial_threshold_pct or overall_result == Trend.BEARISH:
        return Trend.BEARISH
    else:
        return Trend.LINEAR_STABLE

def detectBullishOrBearishCandle(df: pd.DataFrame):
    if df.empty is True:
        logger.info("Warning: Dataframe is empty in detectBullishOrBearishCandle")
        return Trend.LINEAR_STABLE   
    logger.info(df)        
    df = populateTrend(df)
    bullish_threshold_pct = float(get_config("ReverseTrendBullishThresholdPct", 0.7))
    bearish_threshold_pct = float(get_config("ReverseTrendBearishThresholdPct", 0.7))
    bullish_count = df['Trend'].value_counts().get('Bullish', 0)
    bearish_count = df['Trend'].value_counts().get('Bearish', 0)
    total_rows = len(df)
    if bullish_count / total_rows >= bullish_threshold_pct:
        overall_result = Trend.BULLISH
    elif bearish_count / total_rows >= bearish_threshold_pct:
        overall_result = Trend.BEARISH
    else:
        overall_result = Trend.LINEAR_STABLE
    logger.info(f"Overall Result (whole dataframe) Trend: {overall_result}")

    candle_divisor = float(get_config("ReverseTrendCandleDivisor", 3.0))
    partial_length = round(float(total_rows) // candle_divisor)
    if partial_length > 0 and len(df) > partial_length:
        last_partial_df = df[-partial_length:]
        first_partial_df = df[:-partial_length]
        first_partial_result = determineTrend(overall_result, partial_length, first_partial_df)
        last_partial_result = determineTrend(overall_result, partial_length, last_partial_df)
        logger.info(first_partial_df)
        logger.info(f"first_partial_result={first_partial_result}")
        logger.info(last_partial_df)
        logger.info(f"last_partial_result={last_partial_result}")

        # Check the last 3 rows
        last_trend_entries = int(get_config("ReverseTrendLastTrendEntries", 3))
        if last_trend_entries > len(df):
            logger.info(f"Last trends entries {last_trend_entries} is greater than candle length {len(df)} adjusting to candle length")
            update_config("ReverseTrendLastTrendEntries", len(df))
            last_trend_entries = len(df)
        last_trends = df['Trend'].tail(last_trend_entries)
        if all(last_trends == 'Bullish') and overall_result == Trend.BULLISH and last_partial_result == Trend.BULLISH and first_partial_result == Trend.BULLISH:
            overall_result = Trend.BULLISH
        elif all(last_trends == 'Bearish') and overall_result == Trend.BEARISH and last_partial_result == Trend.BEARISH and first_partial_result == Trend.BEARISH:
            overall_result = Trend.BEARISH
        else:
            overall_result = Trend.LINEAR_STABLE
        logger.info(f"End Detect Overall Trend for Dataframe: overall_result={overall_result}")        
        logger.info(f"all(last_trends)={all(last_trends == 'Bullish')}, overall_result={overall_result}, last_partial_result=last_partial_result={last_partial_result}")
        return overall_result
    else:
        logger.info(f"partial_length={partial_length} > 0 and len(df)={len(df)} > partial_length={partial_length} is false, no detectBullishOrBearishCandle")
        return Trend.LINEAR_STABLE

def is_linear_decreasing(profits, symbol: str):
    logger.info(f"Checking if profits are linear decreasing for {symbol}...")
    profit_values = [profit.get("profit", 0) for profit in profits]
    df = pd.DataFrame(profit_values, columns=["current_profit"])
    trend = detectBullishOrBearishCandle(df)
    if trend == Trend.BULLISH or trend == Trend.LINEAR_STABLE:
        return "no", False
    elif trend == Trend.BEARISH:
        return "yes", True
    else:
        return f"cannot determine trend for {symbol} in is_linear_decreasing", False

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
