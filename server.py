import json, os

from flask import Flask, request

from dotenv import load_dotenv

load_dotenv()

def config (str):
    os.getenv(str)

app = Flask(__name__)

from storage import *

from binance_order import *

from telegram_sender import *

from pymongo import MongoClient

db_client = MongoClient(config('MONGODB_URI'))

connect_db(db_client)

from trade_cop import *

def order(side, symbol, order_price, passphrase, order_size, leverage, loss, req_type, strategy, exchange, tp_size):
    try:
        res = "loading"
        print(f"{passphrase} trading {symbol} with {strategy} on {exchange} Sending order - {side} {symbol} at {order_price}.")
        if exchange[0] == "0": #EXCHANGE 0 === BINANCE
            if req_type == "order":
                if side == "BUY":
                    binance_order = binance_long(symbol, leverage, order_size, order_price, loss, exchange, db_client, strategy, passphrase)
                    if binance_order[0] == "success":
                        print(f'Successfully executed long order alert on Binance :)')
                        send_telegram_alert(f'Successfully executed long order alert on Binance :)', config('TG_TOKEN'))
                        res = "success"
                elif side == "SELL":
                    binance_order = binance_short(symbol, leverage, order_size, order_price, loss, exchange, db_client,
                                                 strategy, passphrase)
                    if binance_order[0] == "success":
                        print(f'Successfully executed short order alert on Binance :)')
                        send_telegram_alert(f'Successfully executed short order alert on Binance :)', config('TG_TOKEN'))
                        res = "success"
            elif req_type == "exit":
                position = get_order(db_client, exchange, strategy, symbol)
                res_binance = connect_binance()
                if res_binance[0] == "success":
                    tp_quantity = position['quantity'] * tp_size
                    exit_order = res_binance[1].futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=tp_quantity)
                    cancel_stop_loss = res_binance[1].futures_cancel_order(symbol=symbol, orderId=position['stopLossId'], timestamp=True)
                    if exit_order and cancel_stop_loss:
                        send_telegram_alert(f"Successfully stopped order : {exit_order} {position['quantity']} and cancelled sl : {cancel_stop_loss}", config('TG_TOKEN'))
                        res = "success"
            else:
                print(f" {passphrase} {symbol} Not Executed order - {side} {symbol} at {order_price}.")
        else:
            print(f"Wrong exchange id : {exchange}")
            send_telegram_alert(f"Wrong exchange id : {exchange}", config('TG_TOKEN'))
    except Exception as e:
        print("An exception occured - {}".format(e))
        send_telegram_alert("An exception occured - {}".format(e), config('TG_TOKEN'))
        return False

    print("Request successfully executed")
    return res

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['passphrase'] != config('WEBHOOK_PASSPHRASE'):
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    side = data['side'].upper()
    ticker = data['ticker'].upper()
    tp_size = data['tp_size']
    order_price = data['order_price']
    leverage = data['leverage']
    loss = data['stop_loss']
    order_size = data['order_size']
    req_type = data['req_type']
    strategy = data['strategy']
    exchange = data['exchange']
    order_response = order(side, ticker, order_price, data['passphrase'], order_size, leverage, loss, req_type, strategy, exchange, tp_size)
    if order_response:
        print('Order executed')
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

@app.route('/stream/start', methods=['POST'])
def start_stream ():
    data = json.loads(request.data)
    stop = data["stop"]
    binance_cop(stop)
    return {
        "code": "success",
        "message": "Stream started."
    }

@app.route('/', methods=['GET'])
def render_index ():
    return {
        "message": "work in progress, no user interface so far"
    }