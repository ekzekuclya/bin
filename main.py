import asyncio

from binance.client import Client
import time

api_key = 'VF0OfDcV4eZdPwFeVc4DaydR7Wer1lTVhBCpBwQL6JPoZ1SHHtOZ8POzvdLhwQx6'
api_secret = 'A61J7BLYxEX0RTrgUf1XbzcdoALpWPkxraPBYoc9G2iIKjqMwPJpINkikjWK0HEI'

clientXen = Client(api_key, api_secret)

api_key = "QphglNty1VsSmcbeOAaqolh11ieefb57JECjWcP9dZf1tJ1qPGPCOnvMCyIQcX5X"
api_secret = "C1XIdR2QJa6zNOe7xaR8BiDafvVcxhO1UIivL7zErB1bTeNurRkN6GGbUDkvtBbG"
clientOpium = Client(api_key, api_secret)


import time
from telegram import Bot



telegram_bot = Bot(token='7893620908:AAFYYYU1NxiaZsQGN_U9_p8X5wRp2gDINEM')
chat_id = '-4630400837'  #

def get_balance_usdt(client):
    account_info = client.get_account()
    balance = None
    for asset in account_info['balances']:
        if asset['asset'] == 'USDT':  # Фильтруем по USDT
            balance = float(asset['free'])  # Доступный баланс
            break
    return balance


async def send_telegram_notification(message):
    try:
        await telegram_bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка при отправке уведомления в Telegram: {e}")


async def monitor_balance():
    xenlast_balance_spot = None
    opilast_balance_spot = None
    while True:
        try:
            current_balance_spot_xen = get_balance_usdt(clientXen)
            current_balance_spot_opi = get_balance_usdt(clientOpium)
            if current_balance_spot_xen != xenlast_balance_spot:
                message = f"Баланс Xenezis изменился! Новый баланс: {current_balance_spot_xen:.2f} USDT"
                print(message)
                await send_telegram_notification(message)
                xenlast_balance_spot = current_balance_spot_xen
            if current_balance_spot_opi != opilast_balance_spot:
                message = f"Баланс Opium изменился! Новый баланс: {current_balance_spot_opi:.2f} USDT"
                print(message)
                await send_telegram_notification(message)
                opilast_balance_spot = current_balance_spot_opi
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка при мониторинге баланса: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(monitor_balance())




