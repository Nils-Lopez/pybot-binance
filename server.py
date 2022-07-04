import json, os

from binance.client import Client
from binance.enums import *
from flask import Flask, request
from dotenv import dotenv_values

config = dotenv_values(".env")

app = Flask(__name__)
client = Client(config['BINANCE_APIKEY'], config['BINANCE_SECRET'], tld='us')

def order(side, quantity, symbol, order_price, passphrase, order_type="LIMIT"):
    try:
        print(f"{passphrase} {symbol} Sending order {order_type} - {side} {quantity} {symbol} at {order_price}.")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, timeInForce=timeInForce, price=order_price)
        if order:
            print(
                f" {passphrase} {symbol} Executed order {order}.")
        else:
            print(
                f" {passphrase} {symbol} Not Executed order {order_type} - {side} {quantity} {symbol} at {order_price}.")
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

    if data['passphrase'] != config['BINANCE_APIKEY']:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }
    side = data['side'].upper()
    quantity = data['strategy']['order_contracts']
    ticker = data['ticker'].upper()

    order_response = order(side, quantity, ticker, data['passphrase'])


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