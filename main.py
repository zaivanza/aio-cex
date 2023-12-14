from modules.checker import GetBalance
from modules.trader import Trader
from modules.transfer import Transfer
from modules.withdraw import Withdraw
from modules.titles import TITLE, TITLE_COLOR
import asyncio
from termcolor import cprint

if __name__ == "__main__":

    cprint(TITLE, TITLE_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth', TITLE_COLOR)

    MODULE = int(input('''
MODULE:
1. get balance
2. make trade
3. transfer
4. withdraw

Выберите модуль (1 / 4) : '''))
    
    functions = {
        1: GetBalance, 
        2: Trader,
        3: Transfer,
        4: Withdraw,
    }

    if MODULE in [1, 2, 3, 4]:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(functions[MODULE]().main())
    else:
        cprint('\n>>> Такого модуля нет <<<', 'red')



