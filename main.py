import asyncio
from termcolor import cprint
import inquirer

from modules.checker import GetBalance, GetDepositAddress
from modules.trader import Trader
from modules.transfer import Transfer
from modules.withdraw import Withdraw
from modules.titles import TITLE, TITLE_COLOR

if __name__ == "__main__":
    cprint(TITLE, TITLE_COLOR)
    cprint('\nsubscribe to us : https://t.me/hodlmodeth', TITLE_COLOR)

    questions = [
        inquirer.List('module',
                      message="Выберите модуль (1 / 5)",
                      choices=[
                          ('get balance', 1),
                          ('make trade', 2),
                          ('transfer', 3),
                          ('withdraw', 4),
                          ('get_deposit_address', 5)
                      ],
                      carousel=True)
    ]

    answers = inquirer.prompt(questions)
    MODULE = answers['module']

    functions = {
        1: GetBalance,
        2: Trader,
        3: Transfer,
        4: Withdraw,
        5: GetDepositAddress
    }

    if MODULE in functions:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(functions[MODULE]().main())
    else:
        cprint('\n>>> Такого модуля нет <<<', 'red')
