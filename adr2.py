from helper import *

def adr_strategy(vale_trade_info, valbz_trade_info) -> dict:
    vale_trade_price_list = list(map(lambda x: x[0], vale_trade_info))
    valbz_trade_price_list = list(map(lambda x: x[0], valbz_trade_info))
    if(len(vale_trade_price_list) >= 10 and len(valbz_trade_price_list) >= 10):
        vale = vale_trade_price_list[-10:]
        valbz = valbz_trade_price_list[-10:]
        result = adr_signal(valbz, vale)
        if(result != None and result[0] == True):
            print ("\n------------------------- ADR Trading -------------------------\n")
            size_to_trade = (result[3] - 2) * 2 + 4
            #stuff = result[3] // 2
            return [{"type" : "add", "symbol": "VALE", "dir" : "BUY", "price": result[1]+1, "size": size_to_trade},
                    {"type" : "convert", "symbol": "VALE", "dir" : "SELL", "size": size_to_trade},
                    {"type" : "add", "symbol": "VALBZ", "dir" : "SELL", "price": result[2]-1, "size": size_to_trade}]

#common stock & its ADR pair trading strategy
def adr_signal(cs_trade_price_list, adr_trade_price_list):
    cs_mean = mean(cs_trade_price_list)
    adr_mean = mean(adr_trade_price_list)
    fair_diff = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [True, adr_mean, cs_mean, fair_diff]
