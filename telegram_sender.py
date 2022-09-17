import telegram



def send_telegram_alert (message, token):
    tg_bot = telegram.Bot(token=token)
    print(f"SENDING ALERT : {message}")
    tg_bot.send_message(text=message, chat_id="-1001762191604")
