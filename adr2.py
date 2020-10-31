from helper import *
import pandas as pd
import numpy as np

DATA_TO_CONSIDER = 26

def ema(values, period):
    values = np.array(values)
    return pd.DataFrame(values).ewm(span=period).mean().values[-1][-1]

def adr_strategy(vale_trade_info, valbz_trade_info) -> dict:
    vale_trade_price_list = list(map(lambda x: x[0], vale_trade_info))
    valbz_trade_price_list = list(map(lambda x: x[0], valbz_trade_info))
    if(len(vale_trade_price_list) >= DATA_TO_CONSIDER and len(valbz_trade_price_list) >= DATA_TO_CONSIDER):
        vale = vale_trade_price_list[-DATA_TO_CONSIDER:]
        valbz = valbz_trade_price_list[-DATA_TO_CONSIDER:]
        result = adr_signal(valbz, vale)
        if(result != None and result[0] != None):
            print ("\n------------------------- ADR Trading -------------------------\n")
            if result[0] == "BUY":
                return [{"type" : "add", "symbol": "VALE", "dir" : "BUY", "price": result[1], "size": 10},
                        {"type" : "convert", "symbol": "VALE", "dir" : "SELL", "size": 10}]
            #stuff = result[3] // 2
            elif result[0] == "SELL":
                return [{"type" : "add", "symbol": "VALBZ", "dir" : "SELL", "price": result[2], "size": 10}]

def get_actual_price(cs_price, adr_price):
    return (cs_price + adr_price)/2

prev_diff = None
#common stock & its ADR pair trading strategy
def adr_signal(cs_trade_price_list, adr_trade_price_list):
    global prev_diff
    prices = []
    for i in range(len(cs_trade_price_list)):
        prices.append(get_actual_price(cs_trade_price_list[0], adr_trade_price_list[0]))

    macd26 = ema(prices[-26:], 26)
    macd12 = ema(prices[-12:], 12)
    signal = ema(prices[-9:], 9)

    macd = macd12 - macd26
    diff = macd26 - signal

    cs_mean = mean(cs_trade_price_list[-1:])
    adr_mean = mean(adr_trade_price_list[-1:])

    if prev_diff != None:
        if prev_diff <= 0 and diff > 0:
            return ["BUY", adr_mean, cs_mean, fair_diff]
        elif prev_diff >= 0 and diff < 0:
            return ["SELL", adr_mean, cs_mean, fair_diff]
    prev_diff = diff

    return None
    fair_diff = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [True, adr_mean, cs_mean, fair_diff]
