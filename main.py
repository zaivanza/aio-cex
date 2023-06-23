from setting import EXCHANGES, DATA_FILE_NAME, value_get_balance, value_trade
from modules.checker import main as checker
from modules.trader import main as trader
from modules.helpers import RUN_TEXT, RUN_COLOR
import asyncio
from termcolor import cprint

if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth', RUN_COLOR)

    MODULE = int(input('''
MODULE:
1. get balance
2. make trade

Выберите модуль (1 / 2) : '''))

    check_token = value_get_balance()
    token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time = value_trade()

    if MODULE == 1:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(checker(DATA_FILE_NAME, check_token, EXCHANGES))

    elif MODULE == 2:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(trader(DATA_FILE_NAME, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time, EXCHANGES))

    else:
        cprint('\n>>> такого модуля нет <<<', 'red')



