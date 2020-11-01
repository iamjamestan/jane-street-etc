from typing import List
from etc_types import *

def bond_strategy(buy: List[RestingOrder], sell: List[RestingOrder]) -> List[Trade]:
    """Takes in `buy` and `sell` resting orders and returns trades to perform.
        These trades will need `order_id` to be added separately.

    Args:

        buy (List[RestingOrder]): Resting buy orders of BOND.
        sell (List[RestingOrder]): Resting sell orders of BOND.

    Returns:

        List[Trade]: List of trades to perform. May be empty.
    
    Example:

        >>> bond_strategy([[1001, 4], [999, 8]], [[998, 5], [1002, 7]])
        [{"type": "add", "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 4},
        {"type": "add", "symbol": "BOND", "dir": "BUY", "price": 998, "size": 5}]

    """
    buy_trades = []
    for i in range(len(buy)):
        if buy[i][0] > 1000:
            buy_trades.append({"type": Action.ADD, "symbol": Symbol.BOND, "dir": Direction.SELL, "price": buy[i][0], "size": buy[i][1]})
    sell_trades = []
    for i in range(len(sell)):
        if sell[i][0] < 1000:
            sell_trades.append({"type": Action.ADD, "symbol": Symbol.BOND, "dir": Direction.BUY, "price": sell[i][0], "size": sell[i][1]})
    return buy_trades + sell_trades
