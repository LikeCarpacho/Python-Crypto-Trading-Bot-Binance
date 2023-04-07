import websocket
import json
import talib
import numpy
import config
from binance.client import Client
from binance.enums import *
import ctypes

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) #Makes console invinsible

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_5m"

TRADE_SYMBOL = "Name of crypto pair"
TRADE_QUANTITY = "Quantity you want to buy"
closes = []
highs = []
lows = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    json_message = json.loads(message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    high = candle['h']
    low = candle['l']

    if is_candle_closed:
        print("Candle closed at {}".format(close))
        closes.append(float(close))
        print("Closes")
        print(closes)
        print("Candle high was {}".format(high))
        highs.append(float(high))
        print("Highs")
        print(highs)
        print("Candle low was {}".format(low))
        lows.append(float(low))
        print("Lows")
        print(lows)
            
        if len(closes) > 0:
            np_closes = numpy.array(closes)
            np_highs = numpy.array(highs)
            np_lows = numpy.array(lows)
            Ricochete = (((np_closes[-1]) - (np_lows[-1]))/((np_highs[-1]) - (np_lows[-1])))

            if Ricochete > 90:
                if in_position:
                    order = client.order_market_sell(
                    symbol = TRADE_SYMBOL,
                    quantity = TRADE_QUANTITY)
                    in_position = False
                else:
                    pass
            
            if Ricochete < 10:
                if in_position:
                    pass
                else:
                    order = client.order_market_buy(
                    symbol = TRADE_SYMBOL,
                    quantity = TRADE_QUANTITY)
                    asyncio.run(buy())
                    in_position = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
