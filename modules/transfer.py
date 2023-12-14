from termcolor import cprint
from loguru import logger
import asyncio
from .helpers import get_ccxt_accounts
from setting import DATA_FILE_NAME, EXCHANGES, ValueTransfer

class Transfer:

    def __init__(self) -> None:
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME)
        self.exchanges = EXCHANGES
        self.token = ValueTransfer.token
        self.from_account = ValueTransfer.from_account
        self.to_account = ValueTransfer.to_account

    async def get_transfer(self, ccxt_account, account):
        try:
            balance = await ccxt_account.fetch_balance()
            balance_of_coin = balance[self.token]['free']
        except KeyError as error: # kucoin, bybit
            balance_of_coin = 0
        except Exception as error:
            logger.error(f'{ccxt_account.name} - {account} | error : {error}')
            balance_of_coin = 0

        if balance_of_coin > 0.0001:
            try:
                transfer = await ccxt_account.transfer(
                    self.token, balance_of_coin, self.from_account, self.to_account
                )
                logger.success(f'{ccxt_account.name} - {account} | {self.from_account} => {self.to_account} | {balance_of_coin} {self.token}')

            except Exception as error:
                logger.error(f'{ccxt_account.name} - {account} | transfer error : {error}')

        await ccxt_account.close()
    
    async def main(self): 
        tasks = []
        for items in self.accounts:
            for account, ccxt_account in items.items():
                if (ccxt_account.name in self.exchanges and ccxt_account.name in ['Bybit']):
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.get_transfer(ccxt_account, account))
                    tasks.append(task)

        await asyncio.gather(*tasks)
