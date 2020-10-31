"""input 'buy': [[999, 4], [998, 8]], 'sell': [[1001, 5], [1002, 7]]
 if bond < 1000 buy
 > 1000 sell
returns {"type": "add", "order_id": N, "symbol": "SYM", "dir": "BUY", "price": N, "size": N}"""


def bond_strategy(buy, sell) -> dict:
    if buy and buy[0][0] > 1000:
        buy_trades = []
        for i in range(len(buy)):
            buy_trades.append({"type": "add", "symbol": "BOND", "dir": "SELL", "price": buy[i][0], "size": buy[i][1]})
        return buy_trades
    elif sell and sell[0][0] < 1000:
        sell_trades = []
        for i in range(len(sell)):
            sell_trades.append({"type": "add", "symbol": "BOND", "dir": "BUY", "price": sell[i][0], "size": sell[i][1]})
        return sell_trades
    else:
        return None
