from termcolor import cprint
from loguru import logger
import asyncio
import csv
from tabulate import tabulate
from .helpers import round_to, get_ccxt_accounts
from .okx import OKX
from setting import ValueGetBalance, EXCHANGES, DATA_FILE_NAME

class GetBalance():

    def __init__(self) -> None:
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME)
        self.exchanges = EXCHANGES
        self.balances = []
        self.token = ValueGetBalance.token
        self.type_account = ValueGetBalance.account

    async def get_balance(self, ccxt_account, account):
        '''смотрим баланс всех монет на бирже'''

        try:
            balance = await ccxt_account.fetch_balance()
            balance_of_coin = balance[self.token]['free']
        except KeyError as error: # kucoin, bybit
            balance_of_coin = 0
        except Exception as error:
            logger.error(f'{ccxt_account.name} - {account} | error : {error}')
            balance_of_coin = 0

        if ccxt_account.name not in self.balances:
            self.balances.append(
                {ccxt_account.name: {account: balance_of_coin}}
            )

        await ccxt_account.close()

    def send_results(self):
        file_name = 'balances.csv'

        # записываем в csv
        with open(file_name, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['number', 'exchange', 'account', 'balance'])

            tables = []
            number = 0
            for items in self.balances:

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
    
    async def main(self): 
        tasks = []
        for items in self.accounts:
            for account, ccxt_account in items.items():
                if (ccxt_account.name in self.exchanges and ccxt_account.name != 'OKX'):
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.get_balance(ccxt_account, account))
                    tasks.append(task)

        if 'OKX' in self.exchanges:
            task = asyncio.create_task(OKX().main(data_file_name=DATA_FILE_NAME, balances=self.balances, module=0, balance_token=self.token))
            tasks.append(task)

        await asyncio.gather(*tasks)
        self.send_results()
