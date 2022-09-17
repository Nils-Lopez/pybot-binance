

def connect_db (client):
    try:
        db = client.admin
        # Issue the serverStatus command and print the results
        serverStatusResult = db.command("serverStatus")
        if serverStatusResult:
            print("Mongo Database successfully connected")
    except Exception as e:
        print("An exception occured {}".format(e))


def save_order (db_client, order, quantity, exchange, strategy, symbol, sl):
    try:
        db = db_client.pyBot
        data = {
            "strategy": strategy,
            "exchange": exchange,
            "quantity": quantity,
            "symbol": symbol,
            "order": order,
            "stopLoss": sl
        }
        res = db.orders.insert_one(data)
        print(f'Saving order : {res}')
    except Exception as e:
        print('An exception occured : {}'.format(e))

def get_order (db_client, exchange, strategy, symbol):
    try:
        db = db_client.pyBot
        strat_last_order = db.orders.find({"$and": [{"strategy": strategy}, {"exchange": exchange}, {"symbol": symbol}]}).limit(1).sort([('$natural',-1)])

        print(f'Strat order last one : {strat_last_order}')
        positionSize = "loading"
        for x in strat_last_order :
            quantity = x["quantity"]
            if quantity:
                positionSize = quantity
        if positionSize != "loading":
            return {
                "quantity": positionSize,
                "stopLossId": strat_last_order["stopLoss"]
            }
    except Exception as e:
        print ('An exception occured mgl : {}'.format(e))