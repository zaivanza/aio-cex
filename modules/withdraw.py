from termcolor import cprint
from loguru import logger
import asyncio
import random
from .helpers import get_ccxt_accounts, round_to
from setting import ValueWithdraw, DATA_FILE_NAME, EXCHANGES

class Withdraw:

    def __init__(self) -> None:
        self.symbol = ValueWithdraw.symbol
        self.chain = ValueWithdraw.chain
        self.amounts = ValueWithdraw.amounts
        self.withdraw_all_balance = ValueWithdraw.withdraw_all_balance
        self.fee = ValueWithdraw.fee
        self.min_withdraw = ValueWithdraw.min_withdraw
        self.recipient = ValueWithdraw.recipient
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME)
        self.exchanges = EXCHANGES

    async def withdraw_token(self, ccxt_account, account):

        if self.withdraw_all_balance:
            try:
                balance = await ccxt_account.fetch_balance()
                amount = balance[self.symbol]['free'] - self.fee
            except KeyError as error: # kucoin, bybit
                amount = 0
            except Exception as error:
                logger.error(f'{ccxt_account.name} - {account} | error : {error}')
                amount = 0

        else:
            amount = round(random.uniform(*self.amounts), 6)

        if ccxt_account.name in ['bitget']:
            params = {"chain": self.chain}
        else:
            params = {"network": self.chain}

        if amount > 0 and amount >= self.min_withdraw:
            try:
                amount = round_to(amount)
                withdraw = await ccxt_account.withdraw(
                    code = self.symbol,
                    amount = amount,
                    address = self.recipient,
                    tag = None, 
                    params = params
                )
                logger.success(f'{ccxt_account.name} - {account} | withdraw {amount} {self.symbol} ({self.chain}) => {self.recipient}')

            except Exception as error:
                logger.error(f'{ccxt_account.name} - {account} | withdraw error : {error}')

        await ccxt_account.close()
    
    async def main(self): 
        tasks = []
        for items in self.accounts:
            for account, ccxt_account in items.items():
                if ccxt_account.name != "OKX":
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.withdraw_token(ccxt_account, account))
                    tasks.append(task)

        await asyncio.gather(*tasks)
