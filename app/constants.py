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
    "description": "Retrieve last n seconds in profit array to use for reverse logic ",
    "label": "",
    "value": 1800
  },
  "ReverseTrendCheckMinCount": {
    "description": "Check current profits array last elements",
    "label": "",
    "value": 120
  },
  "SantimentThreshold": {
    "description": "Sentiment threshold to determine signal, over 0.25 = long, less -0.25 = short",
    "label": "",
    "value": 0.25
  },
  "SantimentFromTimeDaysAgo": {
    "description": "Santiment from day to determine signal. (7d minimum)",
    "label": "",
    "value": 7
  },
  "SantimentToTimeDaysAgo": {
    "description": "Santiment to day (0=today)",
    "label": "",
    "value": 0
  },
  "ReturnOnInvest": {
    "description": "Initial ROI for custom_exit",
    "label": "",
    "value": 0.12
  },
  "BiasWeightPaid": {
    "description": "Bias importance weight when calculating final bias for free endpoints, greater 1 are more important",
    "label": "",
    "value": 1
  },
  "BiasWeightFree": {
    "description": "Bias importance weight when calculating final bias for free endpoints",
    "label": "",
    "value": 1
  },
  "BiasAgreementPercent": {
    "description": "Accuracy of bias agreement. 100% means all biases must agree",
    "label": "",
    "value": 100,
    "increment": 5
  },
  "ReverseTrendShouldBeNegativePercent": {
    "description": "Check if all profits in array are negative to determine reverse entry (sell and buy reverse)",
    "label": "",
    "value": 90
  },
  "ReverseTrendCheckFirstGreater": {
    "description": "Check if first profit is greater than last profit to determine reverse entry (sell and buy reverse)",
    "label": "",
    "value": "true"
  },
  "ReverseTrendCheckLinearDecreasing": {
    "description": "Check linear decreasing or not (true or false)",
    "label": "",
    "value": "true"
  },
  "ReverseTrendLinearDecreasingThresholdPercent": {
    "description": "Accuracy of linear decreasing curve",
    "label": "",
    "value": 100
  },
  "WinrateHigh": {
    "description": "Threshold for adjusting stoploss and stake",
    "label": "",
    "value": 0.7
  },
  "WinrateLow": {
    "description": "Threshold for adjusting stoploss and stake",
    "label": "",
    "value": 0.3
  },
  "StoplossWinrateHigh": {
    "description": "Adjustment to stoploss according to winrate. If winrate is higher Winratehigh tighten stoploss",
    "label": "",
    "value": -0.1
  },
  "StoplossWinrateLow": {
    "description": "Adjustment to stoploss according to winrate. If winrate is below WinrateLow increase stoploss",
    "label": "",
    "value": -0.18
  },
  "StoplossWinrateNeutral": {
    "description": "Stoploss used in custom_exit to exit trade, custom_stoploss in strategy returns always -0.99",
    "label": "",
    "value": -0.12
  },
  "MaxStake": {
    "description": "Upper Stake limit when adjusting stake",
    "label": "",
    "value": 1000
  },
  "MinStake": {
    "description": "Lower Stake limit when adjusting stake",
    "label": "",
    "value": 100
  },
  "DefaultStake": {
    "description": "Used to return custom_stake_amout to freqtrade to fullfill trades",
    "label": "Used to return custom_stake_amout to freqtrade to fullfill trades",
    "value": 200
  },
  "StakeIncrementStep": {
    "description": "Used to adjust stake amount according to winrate or lost trade",
    "label": "Used to adjust stake amount according to winrate or lost trade",
    "value": 100
  },
  "Leverage": {
    "description": "High Risk, factor to multipy DefautlStake with to increase stake amount, risk of loosing everything",
    "label": "factor to multipy DefautlStake with to increase stake amount",
    "value": 3
  },
  "BiasSymbols": {
    "description": "Show sentiment for these symbols at the bottom",
    "label": "Show sentiment for these symbols at the bottom",
    "value": "BTC"
  },
  "BiasShowAll": {
    "value": "true",
    "description": "In the current sentiment section, whether to match strategy code (false) or to debug every bias (true)",
    "label": "whether to match strategy code (false) or to debug every bias (true)"
  },
  "CheckProfitSeconds": {
    "description": "CheckProfitSeconds",
    "label": "CheckProfitSeconds",
    "value": 5
  },
  "MinutesPassedForReverseLogic": {
    "description": "Check reversing trade after n minutes",
    "label": "Check reversing trade after n minutes",
    "value": 60
  },
  "ReverseTrendMACDShortWindow": {
    "description": "ReverseTrendMACDShortWindow",
    "label": "ReverseTrendMACDShortWindow",
    "value": 6
  },
  "ReverseTrendMACDLongWindow": {
    "description": "ReverseTrendMACDLongWindow",
    "label": "ReverseTrendMACDLongWindow",
      "value": 26
  },
  "ReverseTrendMACDSignalWindow": {
    "description": "ReverseTrendMACDSignalWindow",
    "label": "ReverseTrendMACDSignalWindow",
      "value": 9
  },
  "ReverseTrendBullishThresholdPct": {
    "description": "ReverseTrendBullishThresholdPct",
    "label": "ReverseTrendBullishThresholdPct",
      "value": 0.7
  },
    "ReverseTrendBullishPartialThresholdPct": {
    "description": "ReverseTrendBullishPartialThresholdPct",
    "label": "ReverseTrendBullishPartialThresholdPct",
        "value": 0.75
    },
    "ReverseTrendBearishThresholdPct": {
    "description": "ReverseTrendBearishThresholdPct",
    "label": "ReverseTrendBearishThresholdPct",
        "value": 0.7
    },
    "ReverseTrendBearishPartialThresholdPct": {
    "description": "ReverseTrendBearishPartialThresholdPct",
    "label": "ReverseTrendBearishPartialThresholdPct",
        "value": 0.75,
        "increment": 0.05
    },
    "ReverseTrendCandleDivisor": {
      "description": "ReverseTrendCandleDivisor",
      "label": "ReverseTrendCandleDivisor",
        "value": 3.0
    },
    "ReverseTrendLastTrendEntries": {
    "description": "ReverseTrendLastTrendEntries",
    "label": "ReverseTrendLastTrendEntries",
        "value": 3
    },
  "MaxReverseAttempts": { 
    "description": "Reverse (sell and buy reverse direction) when stoploss reached or reverse conditions are met (linear decreasing current profit)",
    "label": "Max Reverse Trade Count for a pair, when reached pair will be blacklisted",
    "value": 3
  }
} 
