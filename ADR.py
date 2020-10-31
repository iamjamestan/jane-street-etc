def ADRstrategy(vale_trade_info, valbz_trade_info, orderid) -> dict:
    vale_trade_price_list = list(map(lambda x: x[0], vale_trade_info))
    valbz_trade_price_list = list(map(lambda x: x[0]), valbz_trade_info)
    if(len(vale_trade_price_list) >= 10 and len(valbz_trade_price_list) >= 10):
        vale = vale[-10:]
        valbz = valbz[-10:]
        result = ADRSignal(valbz, vale)
        if(result != None and result[0] == True):
            print ("\n------------------------- ADR Trading -------------------------\n")
            orderid +=1
            return {"type" : "add", "order_id": orderid, "symbol": "VALE", "dir" : "BUY", "price": result[1]+1, "size": 10}
            
            orderid +=1
            return {"type" : "convert", "order_id": orderid, "symbol": "VALE", "dir" : "SELL", "size": 10}

            orderid +=1
            return {"type" : "add", "order_id": orderid, "symbol": "VALBZ", "dir" : "SELL", "price": result[2]-1, "size": 10}




#common stock & its ADR pair trading strategy
def ADRSignal(cs_trade_price_list, adr_trade_price_list):
    cs_mean = mean(cs_trade_price_list)
    adr_mean = mean(adr_trade_price_list)
    fair_diff = cs_mean - adr_mean
    if (fair_diff >= 2):
        return [True, adr_mean, cs_mean]