from termcolor import cprint
from loguru import logger
import asyncio
import csv
from tabulate import tabulate
from .helpers import round_to, get_ccxt_accounts
from .okx import OKX
from setting import ValueGetBalance, ValueGetDepositAddress, DATA_FILE_NAME

class GetBalance():

    def __init__(self) -> None:
        self.exchange = ValueGetBalance.exchange
        self.token = ValueGetBalance.token
        self.type_account = ValueGetBalance.account
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME, self.type_account)
        self.balances = []

    async def get_balance(self, ccxt_account, account):
        '''смотрим баланс всех монет на бирже'''

        attempt = 1
        max_attempt = 3
        while attempt <= max_attempt:
            try:
                balance = await ccxt_account.fetch_balance()
                balance_of_coin = balance[self.token]['free']
                break
            except KeyError as error: # kucoin, bybit
                balance_of_coin = 0
                break
            except Exception as error:
                logger.info(f'[{attempt}/{max_attempt}] {ccxt_account.name} - {account} | error : {error}, try again...')
                await asyncio.sleep(1)
            attempt += 1
        else:
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
                if (ccxt_account.name == self.exchange and ccxt_account.name != 'OKX'):
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.get_balance(ccxt_account, account))
                    tasks.append(task)

        if self.exchange == 'OKX':
            task = asyncio.create_task(OKX().main(data_file_name=DATA_FILE_NAME, balances=self.balances, module=0, balance_token=self.token))
            tasks.append(task)

        await asyncio.gather(*tasks)
        self.send_results()

class GetDepositAddress():

    def __init__(self) -> None:
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME)
        self.exchange = ValueGetDepositAddress.exchange
        self.token = ValueGetDepositAddress.token
        self.chain = ValueGetDepositAddress.chain
        self.addresses = []

    async def get_deposit_address(self, ccxt_account, account):
        '''смотрим депозитный адрес монеты на бирже'''

        try:
            address = await ccxt_account.fetchDepositAddress(self.token, {'network':self.chain})
            address = address["address"]
        except Exception as error:
            logger.error(f'{ccxt_account.name} - {account} | error : {error}')
            address = None

        if ccxt_account.name not in self.addresses:
            self.addresses.append(
                {account: address}
            )

        await ccxt_account.close()

    def send_results(self):
        file_name = 'deposit_addresses.csv'

        # записываем в csv
        with open(file_name, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['number', 'account', 'address'])

            tables = []
            number = 0
            for items in self.addresses:
                for account, address in items.items():
                    number += 1

                    spamwriter.writerow([number, account, address])
                    tables.append([account, address])

            table = tabulate(tables, ['account', 'address'], tablefmt='double_grid')
            cprint(f'\n{table}', 'white')

        cprint(f'Результат записан в {file_name}\n', 'white')
    
    async def main(self): 
        tasks = []
        for items in self.accounts:
            for account, ccxt_account in items.items():
                if (ccxt_account.name == self.exchange and ccxt_account.name != 'OKX'):
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.get_deposit_address(ccxt_account, account))
                    tasks.append(task)

        await asyncio.gather(*tasks)
        self.send_results()