from dotenv import dotenv_values

config = dotenv_values(".env")

def connectDb ():
    try:
        db = client.admin
        # Issue the serverStatus command and print the results
        serverStatusResult = db.command("serverStatus")
        print(serverStatusResult)
    except Exception as e:
        print("An exception occured {}".format(e))


def saveOrder (dbClient, order, quantity, exchange, strategy, symbol):
    try:
        db = dbClient.pyBot
        data = {
            "strategy": strategy,
            "exchange": exchange,
            "quantity": quantity,
            "symbol": symbol,
            "order": order,
        }
        res = db.orders.insert_one(data)
        print(f'Saving order : {res}')
    except Exception as e:
        print('An exception occured : {}'.format(e))

def getOrder (dbClient, exchange, strategy, symbol):
    try:
        db = dbClient.pyBot
        strat_last_order = db.orders.find({"$and": [{"strategy": strategy}, {"exchange": exchange}, {"symbol": symbol}]}).limit(1).sort([('$natural',-1)])

        print(f'Strat order last one : {strat_last_order}')
        for x in strat_last_order :
            quantity = x["quantity"]
            if quantity:
                return quantity

    except Exception as e:
        print ('An exception occure mgl : {}'.format(e))