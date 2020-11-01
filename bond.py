from typing import List
from etc_types import Trade
"""
Takes in `buy` and `sell` arrays and returns an array of trades to perform.
These trades will need `order_id` to be added separately.

Example Input:
`buy` = [[1001, 4], [999, 8]]
`sell` = [[998, 5], [1002, 7]]

Example Output:
[
    { "type": "add", "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 4 },
    { "type": "add", "symbol": "BOND", "dir": "BUY", "price": 998, "size": 5 }
]
"""
def bond_strategy(buy: List[List[int]], sell: List[List[int]]) -> List[Trade]:
    buy_trades = []
    for i in range(len(buy)):
        if buy[i][0] > 1000:
            buy_trades.append({"type": "add", "symbol": "BOND", "dir": "SELL", "price": buy[i][0], "size": buy[i][1]})
    sell_trades = []
    for i in range(len(sell)):
        if sell[i][0] < 1000:
            sell_trades.append({"type": "add", "symbol": "BOND", "dir": "BUY", "price": sell[i][0], "size": sell[i][1]})
    return buy_trades + sell_trades
