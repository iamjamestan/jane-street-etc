from typing import List, Tuple
from helper import *
from etc_types import *

def adr_strategy(vale_trade_info: List[Tuple[int]], valbz_trade_info: List[Tuple[int]]) -> List[Trade]:
    """Takes in the trade data for VALE and VALBZ and returns either `None` or a list of trades to perform.

    This algorithm makes use of simple calculations, such as means and averages. Despite its simplicity, its
        performance turned out to be the best out of all ADR strategies we had, and is the final one employed.

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
        result: List[int] = adr_signal(valbz, vale)
        if result:
            # print ("\n------------------------- ADR Trading -------------------------\n")
            return [{"type" : Action.ADD, "symbol": Symbol.VALE, "dir" : Direction.BUY, "price": result[0] + 1, "size": 10},
                    {"type" : Action.CONVERT, "symbol": Symbol.VALE, "dir" : Direction.SELL, "size": 10},
                    {"type" : Action.ADD, "symbol": Symbol.VALBZ, "dir" : Direction.SELL, "price": result[1] - 1, "size": 10}]
    return []

# Common stock & its ADR pair trading strategy
def adr_signal(cs_trade_price_list: List[int], adr_trade_price_list: List[int]) -> List[int]:
    cs_mean: int = mean(cs_trade_price_list)
    adr_mean: int = mean(adr_trade_price_list)
    fair_diff: int = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [adr_mean, cs_mean]
    return []