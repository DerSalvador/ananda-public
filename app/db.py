import os
from functools import cache
import json
from bias import BiasType
from utils import TimeBasedDeque
from bias import CONFIG_PATH, get_config
from tinydb import TinyDB, Query
from utils import get_logger
from collections import Counter
import numpy as np

logger = get_logger()

#Use in memory store for real sentiments in the last 3 hours
real_sentiments = {}
profits = {}

def update_sentiment(symbol: str, sentiment: str):
    if symbol not in real_sentiments:
        real_sentiments[symbol] = TimeBasedDeque(60*60*2)
    real_sentiments[symbol].add(sentiment)

def is_linear_decreasing(profits, threshold = 95.0):
    if len(profits) < 2:
        return False  # not enough data to compute a line

    x = np.arange(len(profits))
    y = np.array(profits, dtype=np.float64)

    # Fit linear regression line: y = mx + c
    m, c = np.polyfit(x, y, 1)
    y_fit = m * x + c

    # Check if slope is negative (i.e., decreasing)
    m = round(m,2)
    if m >= 0:
        return False

    # Calculate deviation from the line
    deviation = y - y_fit
    deviation = np.round(deviation, 2)
    std_dev = np.std(deviation)

    if std_dev == 0:
        return True  # perfectly linear

    # Count how many points deviate more than one std deviation
    outliers = np.abs(deviation) > std_dev
    percent_outliers = np.sum(outliers) / len(profits) * 100

    return percent_outliers <= 100 - threshold
