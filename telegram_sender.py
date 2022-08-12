import telegram

from dotenv import dotenv_values

config = dotenv_values(".env")

tg_bot = telegram.Bot(token=config['TG_TOKEN'])

def send_telegram_alert (message):
    print(f"SENDING ALERT : {message}")
    tg_bot.send_message(text=message, chat_id="-1001762191604")
