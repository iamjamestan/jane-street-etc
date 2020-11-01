import pandas as pd
import numpy as np

from typing import List, Union
from helper import *
from etc_types import *

DATA_TO_CONSIDER = 26
prev_diff = None
macds: List[float] = []

def ema(values: List[float], period: int) -> float:
    """Calculates exponential moving average for a given list of floats and period."""
    values: np.ndarray = np.array(values)
    return pd.DataFrame(values).ewm(span=period, adjust=False).mean().values[-1][-1]

def adr_strategy(vale_trade_info: List[TradeInfo], valbz_trade_info: List[TradeInfo]) -> List[Trade]:
    """Takes in the trade data for VALE and VALBZ and returns either `None` or a list of trades to perform.

    This algorithm makes use of exponential moving averages.

    Args:

        vale_trade_info (List[TradeInfo]): List of VALE `(price, quantity)` tuples in chronological order.
        valbz_trade_info (List[TradeInfo]): List of VALBZ `(price, quantity)` tuples in chronological order.

    Returns:
    
        List[Trade]: A list of trades to perform. May be empty.

    """
    vale_trade_price_list: List[int] = list(map(lambda x: x[0], vale_trade_info))
    valbz_trade_price_list: List[int] = list(map(lambda x: x[0], valbz_trade_info))
    if len(vale_trade_price_list) >= DATA_TO_CONSIDER and len(valbz_trade_price_list) >= DATA_TO_CONSIDER:
        vale: List[int] = vale_trade_price_list[-DATA_TO_CONSIDER:]
        valbz: List[int] = valbz_trade_price_list[-DATA_TO_CONSIDER:]
        result: List[Union[str, int]] = adr_signal(valbz, vale)
        if(result != None and result[0] != None):
            # print ("\n------------------------- ADR Trading -------------------------\n")
            if result[0] == "BUY":
                return [{"type" : Action.ADD, "symbol": Symbol.VALE, "dir" : Direction.BUY, "price": result[1], "size": 10},
                        {"type" : Action.CONVERT, "symbol": Symbol.VALE, "dir" : Direction.SELL, "size": 10}]
            elif result[0] == "SELL":
                return [{"type" : Action.ADD, "symbol": Symbol.VALBZ, "dir" : Direction.SELL, "price": result[2], "size": 10}]
    return []

# Common stock & its ADR pair trading strategy
def adr_signal(cs_trade_price_list: List[int], adr_trade_price_list: List[int]) -> List[Union[str, int]]:
    global prev_diff, macds
    prices: List[float] = np.mean([cs_trade_price_list, adr_trade_price_list], axis=0).tolist()

    macd26: float = ema(prices[-26:], 26)
    macd12: float = ema(prices[-12:], 12)
    macd: float = macd12 - macd26
    # macds.append(macd)
    macds: List[float] = macds[-9:]
    signal: float = ema(macds, 9)
    diff: float = macd - signal
    cs_mean: int = mean(cs_trade_price_list[-1:])
    adr_mean: int = mean(adr_trade_price_list[-1:])

    if prev_diff != None:
        if prev_diff <= 0 and diff > 0:
            return ["BUY", adr_mean, cs_mean]
        elif prev_diff >= 0 and diff < 0:
            return ["SELL", adr_mean, cs_mean]
    
    prev_diff = diff
    return []

## Unused and incomplete function
def adr_signal_bollinger(cs_trade_price_list: List[int], adr_trade_price_list: List[int]) -> None:
    """Unused and incomplete function. Do not use."""
    global prev_diff, macds
    prices = np.mean([cs_trade_price_list, adr_trade_price_list], axis=0).tolist()

    mean: int = np.mean(prices[-20:])
    std = np.std(prices[-20:])

    bollinger_hi2 = mean + std*2
    bollinger_hi1 = mean + std
    bollinger = mean
    bollinger_hi1 = mean - std
    bollinger_lo2 = mean - std*2

    return
