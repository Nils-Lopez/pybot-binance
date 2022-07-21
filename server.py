import json, os

from binance.client import Client
from binance.um_futures import UMFutures
from flask import Flask, request
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values(".env")

future_client = UMFutures(key=config['BINANCE_APIKEY'], secret=config['BINANCE_SECRET'])

app = Flask(__name__)

client = Client(config['BINANCE_APIKEY'], config['BINANCE_SECRET'], testnet=False)

from storage import *

now = datetime.now()

def order(side, symbol, order_price, passphrase, order_size, leverage, loss, profit):
    try:
        balance = future_client.balance(recvWindow=6000)

        for a in balance:
            if a['asset'] == "USDT":
                balance = a['availableBalance']

        quantity =  round(float(float(balance)*(order_size*0.01)/float(order_price)), 3)
        await client.futures_change_leverage(symbol=symbol, leverage=leverage)
        longSl = round(float(order_price)*(1 - (loss*0.01)), 2)
        longTp = round(float(order_price)*(1 + (profit*0.01)), 2)
        shortSl = round(float(order_price)*(1 + (loss*0.01)), 2)
        shortTp = round(float(order_price)*(1 - (profit*0.01)), 2)
        print(f"{passphrase} {symbol} Sending order - {side} {symbol} at {order_price}. quantity :  {quantity} and balance : {balance}")
        order = client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=quantity, isolated=True)

        if (order):
            print(f" {passphrase} {symbol} Executed order {order}. {now}")

            if side == "BUY":
                slorder = client.futures_create_order(symbol=symbol, side="SELL", type="STOP_MARKET",
                                                      quantity=quantity, stopPrice=longSl)
                print(f" sl : {slorder}")

                tporder = client.futures_create_order(symbol=symbol, side="SELL",
                                                      type="TAKE_PROFIT_MARKET", quantity=quantity,
                                                      stopPrice=longTp)
                print(f" tp : {tporder}")
                if (slorder and tporder):
                    saveOrder(now, slorder, tporder, order, config['GIT_TOKEN'])
            elif side == "SELL":
                print("tsb")
                slorder = client.futures_create_order(symbol=symbol, side="BUY", type="STOP_MARKET",
                                      quantity=quantity, stopPrice=shortSl)
                print(f" sl : {slorder}")
                tporder = client.futures_create_order(symbol=symbol, side="BUY",
                                      type="TAKE_PROFIT_MARKET", quantity=quantity,
                                      stopPrice=shortTp)
                print(f" tp : {tporder}")
                if (slorder and tporder):
                    saveOrder(now, slorder, tporder, order, config['GIT_TOKEN'])
            else:
                print("========================")
                print("Sand request")
                print("========================")
        else:
            # order = client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)

            print(f" {passphrase} {symbol} Not Executed order - {side} {quantity} {symbol} at {order_price}.")
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False

    print("Request successfully executed")
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
    leverage = data['leverage']
    loss = data['stop_loss']
    profit = data['take_profit']
    order_size = data['order_size']
    order_response = order(side, ticker, order_price, data['passphrase'], order_size, leverage, loss, profit)


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