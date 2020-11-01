import numpy as np
import pandas as pd

from typing import List, Tuple, Union
from helper import *
from etc_types import *

def adr_strategy(vale_trade_info: List[Tuple[int]], valbz_trade_info: List[Tuple[int]]) -> List[Trade]:
    """Takes in the trade data for VALE and VALBZ and returns either `None` or a list of trades to perform.

    This algorithm makes use of exponential moving averages.

    Args:
        vale_trade_info (List[Tuple[int]]): List of VALE `(price, quantity)` tuples in chronological order.
        valbz_trade_info (List[Tuple[int]]): List of VALBZ `(price, quantity)` tuples in chronological order.

    Returns:
        List[Trade]: A list of trades to perform. May be empty.

    """
    vale_trade_price_list: List[int] = list(map(lambda x: x[0], vale_trade_info))
    valbz_trade_price_list: List[int] = list(map(lambda x: x[0], valbz_trade_info))
    if len(vale_trade_price_list) >= 10 and len(valbz_trade_price_list) >= 10:
        vale: List[int] = vale_trade_price_list[-10:]
        valbz: List[int] = valbz_trade_price_list[-10:]
        result: List[Union[bool, float]] = adr_signal(valbz, vale)
        if result:
            # print ("\n------------------------- ADR Trading -------------------------\n")
            return [{"type" : Action.ADD, "symbol": Symbol.VALE, "dir" : Direction.BUY, "price": result[1]+1, "size": 10},
                    {"type" : Action.CONVERT, "symbol": Symbol.VALE, "dir" : Direction.SELL, "size": 10},
                    {"type" : Action.ADD, "symbol": Symbol.VALBZ, "dir" : Direction.SELL, "price": result[2]-1, "size": 10}]
    return []

def ema(values: List[float], period: int) -> float:
    """Calculates exponential moving average for a given list of floats and period."""
    values: np.ndarray = np.array(values)
    return pd.DataFrame(values).ewm(span=period, adjust=False).mean().values[-1][-1]

# Common stock & its ADR pair trading strategy
def adr_signal(cs_trade_price_list: List[int], adr_trade_price_list: List[int]) -> List[Union[bool, float]]:
    cs_mean: float = ema(cs_trade_price_list, 10)
    adr_mean: float = ema(adr_trade_price_list, 10)
    fair_diff: float = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [True, adr_mean, cs_mean]
    return []
