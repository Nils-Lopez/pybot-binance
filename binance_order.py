from binance.client import Client
from binance.um_futures import UMFutures
from binance.helpers import round_step_size

from dotenv import dotenv_values

config = dotenv_values(".env")

from storage import  *

from telegram_sender import *

def send_long (client, symbol, leverage, quantity, long_sl, passphrase):
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    order = client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity, isolated=True)
    sl_order = client.futures_create_order(symbol=symbol, side="SELL", type="STOP_MARKET", quantity=quantity,
                                           stopPrice=long_sl)
    if order and sl_order:
        return {
            "type": "error",
            "order": order,
            "sl_order": sl_order
        }
    else:
        print(f' Error while sending order on Binance {symbol} {passphrase} {client}')
        send_telegram_alert(f' Error while sending order on Binance {symbol} {passphrase} {client}')
        return {"error"}

def binance_long (symbol, leverage, order_size, order_price, loss, exchange, db_client, strategy, passphrase):
    res_binance = connect_binance()
    if res_binance[0] == "success":
        binance_client = res_binance[1]
        binance_balance = res_binance[2]
        quantity = round(float(float(binance_balance) * (float(order_size) * 0.01) / float(order_price)), 3)
        long_sl = round(float(order_price) * (1 - (float(loss) * 0.01)), 2)
        res_long = send_long(binance_client, symbol, leverage, quantity, long_sl, passphrase)
        if res_long["type"] == "success":
            order = res_long["order"]
            sl_order = res_long["sl_order"]
            print(f' {passphrase} {symbol} Executed order {order} with sl : {sl_order}.')
            save_order(db_client, order, quantity, exchange, strategy, symbol, sl_order["orderId"])
            return ["success"]


def send_short (client, symbol, leverage, quantity, short_sl, passphrase):
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    order = client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity, isolated=True)
    sl_order = client.futures_create_order(symbol=symbol, side="BUY", type="STOP_MARKET", quantity=quantity, stopPrice=short_sl, closePosition=True)
    if order and sl_order:
        return ["success", order, sl_order]
    else:
        print(f' Error while sending order on Binance {symbol} {passphrase} {client}')
        send_telegram_alert(f' Error while sending order on Binance {symbol} {passphrase} {client}')
        return "error"

def binance_short (symbol, leverage, order_size, order_price, loss, exchange, db_client, strategy, passphrase):
    res_binance = connect_binance()
    if res_binance[0] == "success":
        binance_client = res_binance[1]
        binance_balance = res_binance[2]
        sym = (binance_client.get_symbol_info(symbol=symbol))
        tick = float(sym["filters"][0]["tickSize"])
        quantity = round(float(float(binance_balance) * (float(order_size) * 0.01) / float(order_price)), 3)
        short_sl = round_step_size(float(order_price) * (1 + (float(loss) * 0.01)), tick)
        send_telegram_alert(f"TSB : {symbol} {leverage} {quantity} {short_sl} {passphrase}")
        res_short = send_short(binance_client, symbol, leverage, quantity, short_sl, passphrase)
        if res_short[0] == "success":
            order = res_short[1]
            sl_order = res_short[2]
            print(f' {passphrase} {symbol} Executed order {order} with sl : {sl_order}.')
            send_telegram_alert(f' {passphrase} {symbol} Executed order {order} with sl : {sl_order}.')
            save_order(db_client, order, quantity, exchange, strategy, symbol, sl_order["orderId"])
            return ["success"]

def connect_binance ():
    future_client = UMFutures(key=config['BINANCE_APIKEY'], secret=config['BINANCE_SECRET'])
    print('Binance connected')
    client = Client(config['BINANCE_APIKEY'], config['BINANCE_SECRET'], testnet=False)
    balance = future_client.balance(recvWindow=6000)
    for a in balance:
        if a['asset'] == "USDT":
            balance = a['availableBalance']
    if client and balance:
        return ["success", client, balance]
    else:
        send_telegram_alert("An error occured while connecting to binance api")
        return "error"
