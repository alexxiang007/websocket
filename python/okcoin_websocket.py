import sys
sys.path.insert(0, '/home/pi/GitHub/')

import websocket
import time
import json
from json import dump,loads
import datetime
import hashlib
import zlib
import base64
from gmail import *

api_key=''
secret_key = ""
#business
def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    return  hashlib.md5((sign+'secret_key='+secretKey).encode("utf-8")).hexdigest().upper()
#spot trade
def spotTrade(channel,api_key,secretkey,symbol,tradeType,price='',amount=''):
    params={
      'api_key':api_key,
      'symbol':symbol,
      'type':tradeType
     }
    if price:
        params['price'] = price
    if amount:
        params['amount'] = amount
    sign = buildMySign(params,secretkey)
    finalStr =  "{'event':'addChannel','channel':'"+channel+"','parameters':{'api_key':'"+api_key+"',\
                'sign':'"+sign+"','symbol':'"+symbol+"','type':'"+tradeType+"'"
    if price:
        finalStr += ",'price':'"+price+"'"
    if amount:
        finalStr += ",'amount':'"+amount+"'"
    finalStr+="},'binary':'true'}"
    return finalStr

#spot cancel order
def spotCancelOrder(channel,api_key,secretkey,symbol,orderId):
    params = {
      'api_key':api_key,
      'symbol':symbol,
      'order_id':orderId
    }
    sign = buildMySign(params,secretkey)
    return "{'event':'addChannel','channel':'"+channel+"','parameters':{'api_key':'"+api_key+"','sign':'"+sign+"','symbol':'"+symbol+"','order_id':'"+orderId+"'},'binary':'true'}"

#subscribe trades for self
def realtrades(channel,api_key,secretkey):
   params={'api_key':api_key}
   sign=buildMySign(params,secretkey)
   return "{'event':'addChannel','channel':'"+channel+"','parameters':{'api_key':'"+api_key+"','sign':'"+sign+"'},'binary':'true'}"

# trade for future
def futureTrade(api_key,secretkey,symbol,contractType,price='',amount='',tradeType='',matchPrice='',leverRate=''):
    params = {
      'api_key':api_key,
      'symbol':symbol,
      'contract_type':contractType,
      'amount':amount,
      'type':tradeType,
      'match_price':matchPrice,
      'lever_rate':leverRate
    }
    if price:
        params['price'] = price
    sign = buildMySign(params,secretkey)
    finalStr = "{'event':'addChannel','channel':'ok_futuresusd_trade','parameters':{'api_key':'"+api_key+"',\
               'sign':'"+sign+"','symbol':'"+symbol+"','contract_type':'"+contractType+"'"
    if price:
        finalStr += ",'price':'"+price+"'"
    finalStr += ",'amount':'"+amount+"','type':'"+tradeType+"','match_price':'"+matchPrice+"','lever_rate':'"+leverRate+"'},'binary':'true'}"
    return finalStr

#future trade cancel
def futureCancelOrder(api_key,secretkey,symbol,orderId,contractType):
    params = {
      'api_key':api_key,
      'symbol':symbol,
      'order_id':orderId,
      'contract_type':contractType
    }
    sign = buildMySign(params,secretkey)
    return "{'event':'addChannel','channel':'ok_futuresusd_cancel_order','parameters':{'api_key':'"+api_key+"',\
            'sign':'"+sign+"','symbol':'"+symbol+"','contract_type':'"+contractType+"','order_id':'"+orderId+"'},'binary':'true'}"

#subscribe future trades for self
def futureRealTrades(api_key,secretkey):
    params = {'api_key':api_key}
    sign = buildMySign(params,secretkey)
    return "{'event':'addChannel','channel':'ok_sub_futureusd_trades','parameters':{'api_key':'"+api_key+"','sign':'"+sign+"'},'binary':'true'}"

def on_open(self):
    #subscribe okcoin.com spot ticker
    #self.send("{'event':'addChannel','channel':'ok_sub_spotusd_btc_ticker','binary':'true'}")
    
    self.send("{'event':'addChannel','channel':'ok_sub_spotusd_eth_ticker','binary':'true'}")

    #subscribe okcoin.com future this_week ticker
    #self.send("{'event':'addChannel','channel':'ok_sub_futureusd_btc_ticker_this_week','binary':'true'}")

    #subscribe okcoin.com future depth
    #self.send("{'event':'addChannel','channel':'ok_sub_futureusd_ltc_depth_next_week_20','binary':'true'}")

    #subscrib real trades for self
    #realtradesMsg = realtrades('ok_sub_spotusd_trades',api_key,secret_key)
    #self.send(realtradesMsg)


    #spot trade via websocket
    #spotTradeMsg = spotTrade('ok_spotusd_trade',api_key,secret_key,'ltc_usd','buy_market','1','')
    #self.send(spotTradeMsg)


    #spot trade cancel
    #spotCancelOrderMsg = spotCancelOrder('ok_spotusd_cancel_order',api_key,secret_key,'btc_usd','125433027')
    #self.send(spotCancelOrderMsg)

    #future trade
    #futureTradeMsg = futureTrade(api_key,secret_key,'btc_usd','this_week','','2','1','1','20')
    #self.send(futureTradeMsg)

    #future trade cancel
    #futureCancelOrderMsg = futureCancelOrder(api_key,secret_key,'btc_usd','65464','this_week')
    #self.send(futureCancelOrderMsg)

    #subscrbe future trades for self
    #futureRealTradesMsg = futureRealTrades(api_key,secret_key)
    #self.send(futureRealTradesMsg)
alert_sent = false
alert_interval = 60*60
alert_time = 0

def on_message(self,evt):
    global alert_sent, alert_interval, alert_time
    
    try:
        data = inflate(evt) #data decompress
        high = (loads(data.decode('utf-8')))[0]['data']['high']
        low = (loads(data.decode('utf-8')))[0]['data']['low']
        last = (loads(data.decode('utf-8')))[0]['data']['last']
        vol = (loads(data.decode('utf-8')))[0]['data']['vol']
        time = (loads(data.decode('utf-8')))[0]['data']['timestamp']
        time = datetime.datetime.fromtimestamp(time/1000-4*60*60)
        print("last = {}, high = {}, low = {}, vol= {}, time = {}".format(last,high,low,vol,time))
        if (high<=200) and ((alert_sent = true) or (alert_sent = false and time.time()-alert_time>=alert_interval())):
            send_mail("Alert","ETH price lower than 250.")
            alert_sent = true
            alert_time = time.time()

    except BaseException as e:
        print(e)
        
def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

def on_error(self,evt):
    print (evt)

def on_close(self,evt):
    self.run_forever()
    print ('DISCONNECT')

if __name__ == "__main__":
    url = "wss://real.okcoin.com:10440/websocket/okcoinapi"      #if okcoin.cn  change url wss://real.okcoin.cn:10440/websocket/okcoinapi
    api_key='your api_key which you apply'
    secret_key = "your secret_key which you apply"

    websocket.enableTrace(False)
    if len(sys.argv) < 2:
        host = url
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
