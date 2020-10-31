"""input 'buy': [[999, 4], [998, 8]], 'sell': [[1001, 5], [1002, 7]]
 if bond < 1000 buy
 > 1000 sell
returns {"type": "add", "order_id": N, "symbol": "SYM", "dir": "BUY", "price": N, "size": N}"""


def bond_strategy(buy, sell) -> dict:
    if buy and buy[0][0] > 1000:
        return {"type": "add", "symbol": "BOND", "dir": "SELL", "price": buy[0][0], "size": buy[0][1]}
    elif sell and sell[0][0] < 1000:
        return {"type": "add", "symbol": "BOND", "dir": "BUY", "price": sell[0][0], "size": sell[0][1]}
    else:
        return None
