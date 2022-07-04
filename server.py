import json, os

from binance.client import Client
from binance.um_futures import UMFutures
from flask import Flask, request
from dotenv import dotenv_values

config = dotenv_values(".env")

future_client = UMFutures(key=config['BINANCE_APIKEY'], secret=config['BINANCE_SECRET'])

app = Flask(__name__)
client = Client(config['BINANCE_APIKEY'], config['BINANCE_SECRET'], testnet=False)




def order(side, symbol, order_price, passphrase):
    try:
        balance = future_client.balance(recvWindow=6000)

        for a in balance:
            if a['asset'] == "USDT":
                balance = a['availableBalance']

        quantity =  round(float(float(balance)/5/float(order_price)), 3)

        longSl = round(float(order_price)*0.995, 2)
        longTp = round(float(order_price)*1.01, 2)
        shortSl = round(float(order_price)*1.005, 2)
        shortTp = round(float(order_price)*0.99, 2)
        print(f"{passphrase} {symbol} Sending order - {side} {symbol} at {order_price}. quantity :  {quantity} and balance : {balance}")
        order = client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)

        if order:
            print(f" {passphrase} {symbol} Executed order {order}.")
            if side == "BUY":
                print(f" sl : {longSl}")

                sl_order = client.futures_create_order(symbol=symbol, side="SELL", type="STOP_MARKET", stopPrice=longSl,
                                                       closePosition='true')
                print(f" sl : {sl_order}")
                tp_order = client.futures_create_order(symbol=symbol, side="SELL", type="TAKE_PROFIT_MARKET", stopPrice=longTp,
                                                       closePosition='true')
                print(f" tp : {tp_order}")

            else:
                sl_order = client.futures_create_order(symbol=symbol, side="BUY", type="STOP_LOSS_MARKET", stopPrice=shortSl,
                                                       closePosition='true')
                print(f" sl : {sl_order}")

                tp_order = client.futures_create_order(symbol=symbol, side="BUY", type="TAKE_PROFIT_MARKET", stopPrice=shortTp,
                                                       closePosition='true')
                print(f" tp : {tp_order}")

        else:
            print(f" {passphrase} {symbol} Not Executed order - {side} {quantity} {symbol} at {order_price}.")
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False

    return order


@app.route('/')
def welcome():
    return "<h1>This is my first trading bot</h1>"


@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['passphrase'] != config['WEBHOOK_PASSPHRASE']:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }
    side = data['side'].upper()
    ticker = data['ticker'].upper()
    order_price = data['order_price']
    order_response = order(side, ticker, order_price, data['passphrase'])


    if order_response:
        return {
            "code": "success",
            "message": "Order executed."
        }
    else:
        print("Order Failed.")

        return {
            "code": "error",
            "message": "Order Failed."
        }