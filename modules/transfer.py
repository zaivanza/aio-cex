from termcolor import cprint
from loguru import logger
import asyncio
import ccxt.async_support as ccxt
from .helpers import get_ccxt_accounts

async def get_transfer(ccxt_account, account, token, from_account, to_account):
    '''смотрим баланс всех монет на бирже'''

    try:
        balance = await ccxt_account.fetch_balance()
        balance_of_coin = balance[token]['free']
    except KeyError as error: # kucoin, bybit
        balance_of_coin = 0
    except Exception as error:
        logger.error(f'{ccxt_account.name} - {account} | error : {error}')
        balance_of_coin = 0

    if balance_of_coin > 1:

        try:
            transfer = await ccxt_account.transfer(
                token, balance_of_coin, from_account, to_account
            )
            logger.success(f'{ccxt_account.name} - {account} | {from_account} => {to_account} | {balance_of_coin} {token}')

        except Exception as error:
            logger.error(f'{ccxt_account.name} - {account} | transfer error : {error}')

    await ccxt_account.close()
 
async def main(data_file_name, token, exchanges, from_account, to_account): 

    accounts = get_ccxt_accounts(data_file_name, from_account)

    tasks = []

    for items in accounts:
        for item in items.items():

            account = item[0]
            ccxt_account = item[1]

            if (ccxt_account.name in exchanges and ccxt_account.name in ['Bybit']):
                cprint(f'{ccxt_account.name} - {account}', 'blue')
                task = asyncio.create_task(get_transfer(ccxt_account, account, token, from_account, to_account))
                tasks.append(task)

    await asyncio.gather(*tasks)


