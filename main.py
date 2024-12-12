import time
import asyncio
from binance.client import Client
from telegram import Bot


clientXen = Client(api_key='VF0OfDcV4eZdPwFeVc4DaydR7Wer1lTVhBCpBwQL6JPoZ1SHHtOZ8POzvdLhwQx6', api_secret='A61J7BLYxEX0RTrgUf1XbzcdoALpWPkxraPBYoc9G2iIKjqMwPJpINkikjWK0HEI')
clientOpium = Client(api_key='P4KUQ5fQYEFi3tpxeo73SZxMR5ZgVu7gf1Cn5b7dYX9bbwsZBUFqyLkepTcWnwqY', api_secret='p4ebRVUpW5sFXpRb58n64Arinf0NonKt94B3RhPBG0LRrYz3FxNBBQytxtk3jFKz')
telegram_bot = Bot(token='7893620908:AAFYYYU1NxiaZsQGN_U9_p8X5wRp2gDINEM')  # Инициализация Telegram бота
chat_id = '-4630400837'


def get_non_empty_balances(client):
    account_info = client.get_account()
    balances = []
    for asset in account_info['balances']:
        free_balance = float(asset['free'])
        locked_balance = float(asset['locked'])
        if free_balance > 0 or locked_balance > 0:
            balances.append({
                'asset': asset['asset'],
                'free': free_balance,
                'locked': locked_balance
            })
    return balances


def get_withdraw_history(client):
    try:
        withdrawals = client.get_withdraw_history() or []
        for withdrawal in withdrawals:
            withdrawal['type'] = 'withdraw'  # Добавляем тип операции
        return withdrawals
    except Exception as e:
        print(f"Ошибка при получении истории выводов: {e}")
        return []


async def send_telegram_notification(message):
    try:
        await telegram_bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка при отправке уведомления в Telegram: {e}")


def get_deposit_history(client):
    try:
        deposits = client.get_deposit_history() or []
        for deposit in deposits:
            deposit['type'] = 'deposit'  # Добавляем тип операции
        return deposits
    except Exception as e:
        print(f"Ошибка при получении истории депозитов: {e}")
        return []


def get_all_account_activity(client):
    deposits = get_deposit_history(client)
    withdrawals = get_withdraw_history(client)
    all_activities = deposits + withdrawals
    all_activities = sorted(all_activities, key=lambda x: x.get('insertTime', 0), reverse=True)
    return all_activities


async def monitor_balance_and_activity():
    xen_last_balances = []
    opi_last_balances = []
    xen_last_activity_id = None  # Для отслеживания последней показанной операции Xen
    opi_last_activity_id = None  # Для отслеживания последней показанной операции Opium

    while True:
        try:
            current_balances_xen = get_non_empty_balances(clientXen)
            current_balances_opi = get_non_empty_balances(clientOpium)

            if current_balances_xen != xen_last_balances:
                message = f"Обновление баланса Xenezis:\n" + "\n".join(
                    [f"{balance['asset']}: Свободно {balance['free']:.2f}, Заблокировано {balance['locked']:.2f}"
                     for balance in current_balances_xen]
                )
                print(message)
                await send_telegram_notification(message)
                xen_last_balances = current_balances_xen

            if current_balances_opi != opi_last_balances:
                message = f"Обновление баланса Opium:\n" + "\n".join(
                    [f"{balance['asset']}: Свободно {balance['free']:.2f}, Заблокировано {balance['locked']:.2f}"
                     for balance in current_balances_opi]
                )
                print(message)
                await send_telegram_notification(message)
                opi_last_balances = current_balances_opi

            xen_activities = get_all_account_activity(clientXen)
            opi_activities = get_all_account_activity(clientOpium)

            if xen_activities:
                latest_xen_activity = xen_activities[0]
                xen_activity_id = latest_xen_activity.get('id') or latest_xen_activity.get('txId')
                if xen_activity_id != xen_last_activity_id:
                    message = format_activity_message("Xenezis", latest_xen_activity)
                    print(message)
                    await send_telegram_notification(message)
                    xen_last_activity_id = xen_activity_id

            if opi_activities:
                latest_opi_activity = opi_activities[0]
                opi_activity_id = latest_opi_activity.get('id') or latest_opi_activity.get('txId')

                if opi_activity_id != opi_last_activity_id:
                    message = format_activity_message("Opium", latest_opi_activity)
                    print(message)
                    await send_telegram_notification(message)
                    opi_last_activity_id = opi_activity_id

            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка при мониторинге баланса и активности: {e}")
            await asyncio.sleep(30)


def format_activity_message(account_name, activity):
    activity_type = "Ввод" if activity['type'] == 'deposit' else "Вывод"
    status = "Успешно" if activity['status'] in [1, 6] else "Ожидается"
    if 'insertTime' in activity:
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(activity['insertTime'] / 1000))
    else:
        time_str = "Не указано"
    return (f"Новая операция на аккаунте {account_name}: {activity_type} средств\n"
            f"ID транзакции: {activity['txId']}\n"
            f"Актив: {activity['coin']}\n"
            f"Сумма: {activity['amount']}\n"
            f"Сеть: {activity['network']}\n"
            f"Кошелёк: {activity['address']}\n"
            f"Время: {time_str}\n"
            f"Статус: {status}")


if __name__ == "__main__":
    asyncio.run(monitor_balance_and_activity())




