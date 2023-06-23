from termcolor import cprint
from loguru import logger
import asyncio
import csv
import ccxt.async_support as ccxt
from tabulate import tabulate
from .helpers import round_to, get_ccxt_accounts
from .okx import main as okx

balances = []
async def get_balance(ccxt_account, account, token):
    '''смотрим баланс всех монет на бирже'''

    try:
        balance = await ccxt_account.fetch_balance()
        balance_of_coin = balance[token]['free']
    except KeyError as error: # kucoin, bybit
        balance_of_coin = 0
    except Exception as error:
        logger.error(f'{ccxt_account.name} - {account} | error : {error}')
        balance_of_coin = 0

    if ccxt_account.name not in balances:
        balances.append(
            {ccxt_account.name: {account: balance_of_coin}}
        )

    await ccxt_account.close()

def send_results():

    file_name = 'balances.csv'

    # записываем в csv
    with open(file_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow(['number', 'exchange', 'account', 'balance'])

        tables = []

        number = 0
        for items in balances:

            for items in items.items():
                exchange = items[0]

                for items in items[1].items():
                    number += 1

                    account = items[0]
                    balance = round_to(items[1])

                    spamwriter.writerow([number, exchange, account, balance])
                    tables.append([exchange, account, balance])

        # считаем баланс на всех биржах и аккаунтах
        balance = 0
        for item in tables:
            balance = item[2] + balance

        table = tabulate(tables, ['exchange', 'account', 'balance'], tablefmt='double_grid')
        cprint(f'\n{table}', 'white')
        cprint(f'\ntotal balance : {round_to(balance)}\n', 'blue')
        spamwriter.writerow([])
        spamwriter.writerow(['total balance', round_to(balance)])

    cprint(f'Результат записан в {file_name}\n', 'white')
 
async def main(data_file_name, token, exchanges): 

    accounts = get_ccxt_accounts(data_file_name)

    tasks = []

    for items in accounts:
        for item in items.items():

            account = item[0]
            ccxt_account = item[1]

            if (ccxt_account.name in exchanges and ccxt_account.name != 'OKX'):
                cprint(f'{ccxt_account.name} - {account}', 'blue')
                task = asyncio.create_task(get_balance(ccxt_account, account, token))
                tasks.append(task)

    task = asyncio.create_task(okx(data_file_name=data_file_name, balances=balances, module=0, balance_token=token))
    tasks.append(task)

    await asyncio.gather(*tasks)

    send_results()
