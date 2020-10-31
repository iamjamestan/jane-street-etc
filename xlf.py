"""
Use the more liquid basket items to evaluate XLF pricing
if basket items sell < xlf buy -> buy basket items, convert, sell xlf
if basket items buy > xlf sell -> buy xlf, convert, sell basket items
'buy': [[999, 4], [998, 8]], 'sell': [[1001, 5], [1002, 7]]
"""
def xlf_strategy(bond, gs, ms, wfc, xlf):
    if not (bond and gs and ms and wfc and xlf):
        return None

    def _calc_xlf_value(bond, gs, ms, wfc, direction):  # direction = buy or sell
        return 3 * bond[direction][0][0] + 2 * gs[direction][0][0] + 3 * ms[direction][0][0] + 2 * wfc[direction][0][0]

    def _execute_basket_items(bond, gs, ms, wfc, direction):
        reverse_direction = 'BUY' if direction == 'SELL' else 'SELL'
        return [{"type": "add", "symbol": "BOND", "dir": direction,
                 "price": bond[reverse_direction][0][0], "size": 3},
                {"type": "add", "symbol": "GS", "dir": direction,
                    "price": gs[reverse_direction][0][0], "size": 2},
                {"type": "add", "symbol": "MS", "dir": direction,
                    "price": ms[reverse_direction][0][0], "size": 3},
                {"type": "add", "symbol": "WFC", "dir": direction,
                    "price": wfc[reverse_direction][0][0], "size": 2},
                ]

    if _calc_xlf_value(bond, gs, ms, wfc, 'sell') < (xlf['BUY'][0][0] * 10 + 100):
        return _execute_basket_items(bond, gs, ms, wfc, 'BUY') + [
            {"type": "convert", "symbol": "XLF", "dir": "BUY", "size": 10},
            {"type": "add", "symbol": "XLF", "dir": 'SELL',
             "price": xlf['BUY'][0][0], "size": 10},
        ]
    elif _calc_xlf_value(bond, gs, ms, wfc, 'BUY') > (xlf['SELL'][0][0] * 10 + 100):
        return [
            {"type": "add", "symbol": "XLF", "dir": 'BUY',
             "price": xlf['SELL'][0][0], "size": 10},
            {"type": "convert", "symbol": "XLF", "dir": "SELL", "size": 10},
        ] + _execute_basket_items(bond, gs, ms, wfc, 'SELL')
