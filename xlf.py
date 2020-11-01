import pandas as pd

from typing import List
from etc_types import *

def xlf_strategy(gs: RestingDict, ms: RestingDict, wfc: RestingDict, xlf: RestingDict) -> List[Trade]:
    """Uses the more liquid basket items to evaluate XLF pricing, and returns a list of trades to make.

    If basket items sell < XLF buy, then we will buy the basket items, convert, and sell XLF. If the
        basket items buy > XLF sell, then we will buy XLF, convert, and sell the basket items.

    For all arguments, the format will be a dictionary with keys `"BUY"` and `"SELL"`, and the values
        will be lists of resting orders.

    Args:
        gs (RestingDict): Dictionary of GS resting orders.
        ms (RestingDict): Dictionary of MS resting orders.
        wfc (RestingDict): Dictionary of WFC resting orders.
        xlf (RestingDict): Dictionary of XLF resting orders.

    Returns:
        List[Trade]: List of trades to make. May be empty.

    """
    if not (gs and ms and wfc and xlf):
        return []
    for direction in [Direction.BUY, Direction.SELL]:
        if not (gs[direction] and ms[direction] and wfc[direction] and xlf[direction]):
            return []

    def _calc_xlf_value(gs: RestingDict, ms: RestingDict, wfc: RestingDict, direction: str) -> int:  # direction = buy or sell
        return 3 * 1000 + 2 * gs[direction][0][0] + 3 * ms[direction][0][0] + 2 * wfc[direction][0][0]

    def _execute_basket_items(gs: RestingDict, ms: RestingDict, wfc: RestingDict, direction: str) -> List[Trade]:
        reverse_direction = Direction.BUY if direction == Direction.SELL else Direction.SELL
        return [
            {"type": Action.ADD, "symbol": Symbol.GS, "dir": direction,
             "price": gs[reverse_direction][0][0], "size": 2},
            {"type": Action.ADD, "symbol": Symbol.MS, "dir": direction,
             "price": ms[reverse_direction][0][0], "size": 3},
            {"type": Action.ADD, "symbol": Symbol.WFC, "dir": direction,
             "price": wfc[reverse_direction][0][0], "size": 2},
        ]

    if _calc_xlf_value(gs, ms, wfc, Direction.SELL) + 102 < (xlf[Direction.BUY][0][0] * 10):
        return _execute_basket_items(gs, ms, wfc, Direction.BUY) + [
            {"type": Action.CONVERT, "symbol": Symbol.XLF, "dir": Direction.BUY, "size": 10},
            {"type": Action.ADD, "symbol": Symbol.XLF, "dir": Direction.SELL,
             "price": xlf[Direction.BUY][0][0], "size": 10},
        ]
    elif _calc_xlf_value(gs, ms, wfc, Direction.BUY) > (xlf[Direction.SELL][0][0] * 10 + 102):
        return [
            {"type": Action.ADD, "symbol": Symbol.XLF, "dir": Direction.BUY,
             "price": xlf[Direction.SELL][0][0], "size": 10},
            {"type": Action.CONVERT, "symbol": Symbol.XLF, "dir": Direction.SELL, "size": 10},
        ] + _execute_basket_items(gs, ms, wfc, Direction.SELL)
    return []

"""
Same as xlf_strategy but uses time series of trade value in etf basket to calculate xlf value
all inputs are in df
eg: bond
PRICE | QTY
t0    | t0
t1    | t1
t2    | t2
t3    | t3
t4    | t4
"""


def xlf_ema_strategy(gs: RestingDict, ms: RestingDict, wfc: RestingDict, xlf: RestingDict, 
    gs_df: pd.DataFrame, ms_df: pd.DataFrame, wfc_df: pd.DataFrame, xlf_df: pd.DataFrame) -> List[Trade]:
    """Same as `xlf_strategy` but uses time series of trade values in ETF basket to calculate the XLF value.
        This strategy is not used in the final algorithm as it conflicts with the other XLF strategy and was
        too conservative for the profits we were looking to make.

    The `pd.DataFrame` inputs all have the following columns: `"price"` and `"qty"`.

    Args:
        gs (RestingDict): Dictionary of GS resting orders.
        ms (RestingDict): Dictionary of MS resting orders.
        wfc (RestingDict): Dictionary of WFC resting orders.
        xlf (RestingDict): Dictionary of XLF resting orders.
        gs_df (pd.DataFrame): DataFrame of GS trades.
        ms_df (pd.DataFrame): DataFrame of MS trades.
        wfc_df (pd.DataFrame): DataFrame of WFC trades.
        xlf_df (pd.DataFrame): DataFrame of XLF trades.

    Returns:
        List[Trade]: List of trades to make. This list may be empty.

    """
    span: int = 5
    if not (gs and ms and wfc and xlf and len(gs_df) >= span and \
        len(ms_df) >= span and len(wfc_df) >= span and len(xlf_df) >= span):
        return []
    for direction in [Direction.BUY, Direction.SELL]:
        if not (gs[direction] and ms[direction] and wfc[direction] and xlf[direction]):
            return []
    for col in ['price', 'qty']:
        if gs_df[col].empty or ms_df[col].empty or wfc_df[col].empty or xlf_df[col].empty:
            return []

    def _calc_xlf_value(gs_df: pd.DataFrame, ms_df: pd.DataFrame, wfc_df: pd.DataFrame) -> float:
        gs_ema: float = gs_df.ewm(span=span, adjust=False).mean().iloc[-1, 0]
        ms_ema: float = ms_df.ewm(span=span, adjust=False).mean().iloc[-1, 0]
        wfc_ema: float = wfc_df.ewm(span=span, adjust=False).mean().iloc[-1, 0]

        return 3 * 1000 + 2 * gs_ema + 3 * ms_ema + 2 * wfc_ema

    def _execute_basket_items(gs: RestingDict, ms: RestingDict, wfc: RestingDict, direction: str):
        reverse_direction: str = Direction.BUY if direction == Direction.SELL else Direction.SELL
        buffer: int = 1 if direction == Direction.BUY else -1

        return [
            {"type": Action.ADD, "symbol": Symbol.GS, "dir": direction,
             "price": gs[reverse_direction][0][0] + buffer, "size": 2},
            {"type": Action.ADD, "symbol": Symbol.MS, "dir": direction,
             "price": ms[reverse_direction][0][0] + buffer, "size": 3},
            {"type": Action.ADD, "symbol": Symbol.WFC, "dir": direction,
             "price": wfc[reverse_direction][0][0] + buffer, "size": 2},
        ]

    if _calc_xlf_value(gs_df, ms_df, wfc_df) + 102 < (xlf[Direction.BUY][0][0] * 10):
        return _execute_basket_items(gs, ms, wfc, Direction.BUY) + [
            {"type": Action.CONVERT, "symbol": Symbol.XLF, "dir": Direction.BUY, "size": 10},
            {"type": Action.ADD, "symbol": Symbol.XLF, "dir": Direction.SELL,
             "price": xlf[Direction.BUY][0][0], "size": 10},
        ]
    elif _calc_xlf_value(gs_df, ms_df, wfc_df) > (xlf[Direction.SELL][0][0] * 10 + 102):
        return [
            {"type": Action.ADD, "symbol": Symbol.XLF, "dir": Direction.BUY,
             "price": xlf[Direction.SELL][0][0], "size": 10},
            {"type": Action.CONVERT, "symbol": Symbol.XLF, "dir": Direction.SELL, "size": 10},
        ] + _execute_basket_items(gs, ms, wfc, Direction.SELL)
