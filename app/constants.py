from enum import Enum

class configType(str, Enum):
    text = "text"
    boolean = "boolean"
    percent100 = "percent100"
    percent1 = "percent1"

DEFAULT_CONFIG ={
  "GreedAndFearLimit": {
    "description": "No of entries to fetch from the API for Greed and Fear",
    "label": "Greed and Fear Limit",
    "value": 10
  },
  "ReverseTrendCheckBackSeconds": {
    "value": 1800
  },
  "ReverseTrendCheckMinCount": {
    "value": 120
  },
  "SantimentThreshold": {
    "value": 0.25
  },
  "SantimentFromTimeDaysAgo": {
    "value": 7
  },
  "SantimentToTimeDaysAgo": {
    "value": 0
  },
  "ReturnOnInvest": {
    "value": 0.12
  },
  "BiasWeightPaid": {
    "value": 2
  },
  "BiasWeightFree": {
    "value": 1
  },
  "BiasAgreementPercent": {
    "value": 80,
    # "type": configType.percent100,
    "increment": 5,
  },
  "ReverseTrendShouldBeNegativePercent": {
    "value": 90
  },
  "ReverseTrendCheckFirstGreater": {
    "value": "true",
    "type": configType.boolean,
  },
  "ReverseTrendCheckLinearDecreasing": {
    "value": "true",
    "type": configType.boolean,
  },
  "ReverseTrendLinearDecreasingThresholdPercent": {
    "value": 95
  },
  "WinrateHigh": {
    "value": 0.7
  },
  "WinrateLow": {
    "value": 0.3
  },
  "StoplossWinrateHigh": {
    "value": -0.1
  },
  "StoplossWinrateLow": {
    "value": -0.18
  },
  "StoplossWinrateNeutral": {
    "value": -0.12
  },
  "MaxStake": {
    "value": 1000
  },
  "MinStake": {
    "value": 100
  },
  "DefaultStake": {
    "value": 200
  },
  "StakeIncrementStep": {
    "value": 100
  },
  "Leverage": {
    "value": 3
  },
  "BiasSymbols": {
    "value": "BTC"
  },
  "BiasShowAll": {
    "value": "true",
    "Description": "In the current sentiment section, whether to match strategy code (false) or to debug every bias (true)",
    "type": configType.boolean
  },
  "CheckProfitSeconds": {
    "value": 5
  },
  "MinutesPassedForReverseLogic": {
    "value": 60
  },
  "ReverseTrendMACDShortWindow": {
    "value": 6
  },
  "ReverseTrendMACDLongWindow": {
      "value": 26
  },
  "ReverseTrendMACDSignalWindow": {
      "value": 9
  },
  "ReverseTrendBullishThresholdPct": {
      "value": 0.7
  },
    "ReverseTrendBullishPartialThresholdPct": {
        "value": 0.75
    },
    "ReverseTrendBearishThresholdPct": {
        "value": 0.7
    },
    "ReverseTrendBearishPartialThresholdPct": {
        "value": 0.75,
        # "type": configType.percent1,
        "increment": 0.05,
    },
    "ReverseTrendCandleDivisor": {
        "value": 3.0
    },
    "ReverseTrendLastTrendEntries": {
        "value": 3
    }
} 
