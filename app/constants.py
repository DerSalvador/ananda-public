from enum import Enum

class configType(str, Enum):
    text = "text"
    boolean = "boolean"
    percent100 = "percent100"
    percent1 = "percent1"

DEFAULT_CONFIG ={
  "TradeAgeInMinutes": {
    "description": "Past Minutes of last trade to check if made profit, if yes continue with same direction, if no reverse trade",
    "label": "0. TradeAgeInMinutes",
    "value": 20
  },  
  "StoplossWinrateNeutral": {
    "description": "Stoploss used in custom_exit to exit trade, custom_stoploss in strategy returns always -0.99",
    "label": "1. StoplossWinrateNeutral (Default Stoploss), also ROI=Stoploss+0.02",
    "value": -0.05
  },
  "DefaultStake": {
    "description": "Used to return custom_stake_amout to freqtrade to fullfill trades",
    "label": "2. DefaultStake",
    "value": 200
  },
  "StakeIncrementStep": {
    "description": "Used to adjust stake amount according to winrate or lost trade",
    "label": "3. StakeIncrementStep",
    "value": 50
  },
  "Leverage": {
    "description": "High Risk, factor to multipy DefautlStake with to increase stake amount, risk of loosing everything",
    "label": "4. Leverage",
    "value": 3
  },
  "MinutesPassedForReverseLogic": {
    "description": "Check reversing trade after n minutes",
    "label": "5. MinutesPassedForReverseLogic",
    "value": 60
  },
  "MaxReverseAttempts": { 
    "description": "Reverse (sell and buy reverse direction) when stoploss reached or reverse conditions are met (linear decreasing current profit)",
    "label": "6. MaxReverseAttempts",
    "value": 3
  },
  "BannedMinutes": { 
    "description": "Banned minutes after too many reverses",
    "label": "7. BannedMinutes",
    "value": 30
  },
  "ROIOffset": { 
    "description": "Will be added to the stoploss as resulting ROI, so if stoploss is -0.12 and roi_offset 0.02 will be added, ROI will be 0.14 in case of winrate high. In Case of winrate low, stoploss will be -0.1 to realite profit earlier",
    "label": "8. ROI Offset (used to calculate ROI based on stoploss and winrate)",
    "value": 0.01
  },
  "StoplossOffset": { 
    "description": "Will increase stoploss towards 0, in case of winrate high get out earlier. In Case of winrate low, decrease stoploss to allow more losses",
    "label": "9. Stoploss Offset (adapt stoploss according to winrate)",
    "value": 0.005
  },
  "ROIFromConfig": {
    "description": "Initial ROI for custom_exit",
    "label": "91. StoplossFromConfig",
    "value": "true"
  },
  "StoplossFromConfig": {
    "description": "Initial ROI for custom_exit",
    "label": "91. StoplossFromConfig",
    "value": "true"
  },
  "ReturnOnInvest": {
    "description": "Initial ROI for custom_exit",
    "label": "90. ReturnOnInvest",
    "value": 0.07
  },  
  "GreedAndFearLimit": {
    "description": "No of entries to fetch from the API for Greed and Fear",
    "label": "Greed and Fear Limit",
    "value": 10
  },
  "ReverseTrendCheckBackSeconds": {
    "description": "Retrieve last n seconds in profit array to use for reverse logic ",
    "label": "ReverseTrendCheckBackSeconds",
    "value": 1800
  },
  # "ReverseTrendCheckMinCount": {
  #   "description": "Check current profits array last elements",
  #   "label": "ReverseTrendCheckMinCount",
  #   "value": 120
  # },
  "SantimentThreshold": {
    "description": "Sentiment threshold to determine signal, over 0.25 = long, less -0.25 = short",
    "label": "SantimentThreshold",
    "value": 0.25
  },
  # "SantimentFromTimeDaysAgo": {
  #   "description": "Santiment from day to determine signal. (7d minimum)",
  #   "label": "SantimentFromTimeDaysAgo",
  #   "value": 7
  # },
  # "SantimentToTimeDaysAgo": {
  #   "description": "Santiment to day (0=today)",
  #   "label": "SantimentToTimeDaysAgo",
  #   "value": 0
  # },
  # "ReturnOnInvest": {
  #   "description": "Initial ROI for custom_exit",
  #   "label": "ReturnOnInvest",
  #   "value": 0.12
  # },
  "BiasWeightPaid": {
    "description": "Bias importance weight when calculating final bias for free endpoints, greater 1 are more important",
    "label": "BiasWeightPaid",
    "value": 1
  },
  "BiasWeightFree": {
    "description": "Bias importance weight when calculating final bias for free endpoints",
    "label": "BiasWeightFree",
    "value": 1
  },
  "BiasAgreementPercent": {
    "description": "Accuracy of bias agreement. 100% means all biases must agree",
    "label": "BiasAgreementPercent",
    "value": 100,
    "increment": 5
  },
  "ReverseTrendShouldBeNegativePercent": {
    "description": "Check if all profits in array are negative to determine reverse entry (sell and buy reverse)",
    "label": "ReverseTrendShouldBeNegativePercent",
    "value": 100
  },
  "ReverseTrendCheckFirstGreater": {
    "description": "Check if first profit is greater than last profit to determine reverse entry (sell and buy reverse)",
    "label": "ReverseTrendCheckFirstGreater",
    "value": "true"
  },
  "ReverseTrendCheckLinearDecreasing": {
    "description": "Check linear decreasing or not (true or false)",
    "label": "ReverseTrendCheckLinearDecreasing",
    "value": "true"
  },
  "ReverseTrendLinearDecreasingThresholdPercent": {
    "description": "Accuracy of linear decreasing curve",
    "label": "ReverseTrendLinearDecreasingThresholdPercent",
    "value": 100
  },
  "WinrateHigh": {
    "description": "Threshold for adjusting stoploss and stake",
    "label": "WinrateHigh",
    "value": 0.8
  },
  "WinrateLow": {
    "description": "Threshold for adjusting stoploss and stake",
    "label": "WinrateLow",
    "value": 0.6
  },
  "StoplossWinrateHigh": {
    "description": "Adjustment to stoploss according to winrate. If winrate is higher Winratehigh tighten stoploss",
    "label": "StoplossWinrateHigh",
    "value": -0.1
  },
  "StoplossWinrateLow": {
    "description": "Adjustment to stoploss according to winrate. If winrate is below WinrateLow increase stoploss",
    "label": "StoplossWinrateLow",
    "value": -0.18
  },
  "MaxStake": {
    "description": "Upper Stake limit when adjusting stake",
    "label": "MaxStake",
    "value": 1000
  },
  # "SecureProfitInterval": {
  #   "description": "SecureProfitInterval step when to place a stop limit order to secure profit until roi",
  #   "label": "SecureProfitInterval",
  #   "value": 0.001
  # },
  # "StoplimitSlippage": {
  #   "description": "The limit ratio calculated from triggerprice to trigger secure profit limit order, stop limit price must be less than market price",
  #   "label": "StoplimitSlippage",
  #   "value": 0.02
  # },

  "MinStake": {
    "description": "Lower Stake limit when adjusting stake",
    "label": "MinStake",
    "value": 100
  },
  "BiasSymbols": {
    "description": "Show sentiment for these symbols at the bottom",
    "label": "BiasSymbols",
    "value": "BTC"
  },
  "BiasShowAll": {
    "value": "true",
    "description": "In the current sentiment section, whether to match strategy code (false) or to debug every bias (true)",
    "label": "BiasShowAll"
  },
  "CheckProfitSeconds": {
    "description": "CheckProfitSeconds",
    "label": "CheckProfitSeconds",
    "value": 5
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
    "ReverseTrendBanSeconds": {
        "description": "Ban pair for n seconds after max reverse attempts reached",
        "label": "Max reverse ban time (seconds)",
        "value": 60*20
    }
} 
