from termcolor import cprint
import asyncio
from loguru import logger
from .helpers import round_to, get_ccxt_accounts
from .okx import OKX

from setting import DATA_FILE_NAME, EXCHANGES, ValueTrade

class Trader():

    def __init__(self) -> None:
        self.accounts = get_ccxt_accounts(DATA_FILE_NAME)
        self.exchanges = EXCHANGES
        self.token_sell = ValueTrade.token_sell
        self.token_buy = ValueTrade.token_buy
        self.amount = ValueTrade.amount
        self.all_balance = ValueTrade.all_balance
        self.price = ValueTrade.price
        self.is_market_price = ValueTrade.is_market_price
        self.spread = ValueTrade.spread
        self.min_price = ValueTrade.min_price
        self.breaker = ValueTrade.breaker
        self.min_sell = ValueTrade.min_sell
        self.cancel_order = ValueTrade.cancel_order
        self.cl_order_time = ValueTrade.cl_order_time

    async def make_trade(self, ccxt_account, account):
        while True:
            try:
                # смотрим изначальный баланс для просчета разницы (профита)
                check_balance = await ccxt_account.fetch_balance()
                try: start_balance_tokenSell = check_balance[self.token_sell]['free']
                except: start_balance_tokenSell = 0
                try: start_balance_tokenBuy  = check_balance[self.token_buy]['free']
                except: start_balance_tokenBuy  = 0

                if self.token_sell == 'USDT': pair = f'{self.token_buy}/USDT'
                if self.token_buy == 'USDT': pair = f'{self.token_sell}/USDT'

                # check balance
                check_balance   = await ccxt_account.fetch_balance()
                try:    balance_of_coin = round_to(check_balance[self.token_sell]['free'])
                except: balance_of_coin = 0
                logger.info(f'{ccxt_account.name} - {account} | balance of {self.token_sell} : {balance_of_coin}')

                if self.is_market_price:
                    while True:
                        try:
                            # check book of pair 
                            order_book = await ccxt_account.fetch_order_book(pair)
                            order_bids = order_book['bids'][0][0]
                            order_asks = order_book['asks'][0][0]

                            if self.token_sell == 'USDT' : price_to_order = order_asks + order_asks * (self.spread / 100)
                            elif self.token_buy == 'USDT': price_to_order = order_bids - order_bids * (self.spread / 100)
                            break
                        except Exception as error:
                            logger.error(f'{ccxt_account.name} - {account} | ckeck_price error : {error}')
                            await asyncio.sleep(0.5)

                else: 
                    price_to_order = self.price

                if price_to_order >= self.min_price:
                    if balance_of_coin >= self.min_sell:
                        try:
                            if self.all_balance:
                                amount = balance_of_coin * 0.9999 # умножаем на 0.9999 тк может возникнуть ошибка с балансом

                            # make order
                            if self.token_sell == 'USDT':
                                order = await ccxt_account.create_limit_buy_order(
                                    symbol = pair,
                                    amount = amount / price_to_order,
                                    price  = price_to_order,
                                    params = {}
                                )

                            elif self.token_buy == 'USDT':
                                    order = await ccxt_account.create_limit_sell_order(
                                        symbol = pair,
                                        amount = amount, 
                                        price  = price_to_order,
                                        params = {}
                                    )

                            # смотрим статус ордера : open / closed 
                            order_status = await ccxt_account.fetch_order_status(id=order['id'], symbol=pair)

                            if order_status != 'open':

                                # смотрим баланс после трейда для подсчета разницы (профита)
                                check_balance = await ccxt_account.fetch_balance()
                                try:        finish_balance_tokenSell = check_balance[self.token_sell]['free']
                                except :    finish_balance_tokenSell = 0
                                try:        finish_balance_tokenBuy  = check_balance[self.token_buy]['free']
                                except :    finish_balance_tokenBuy  = 0

                                result_token_sell   = round_to(start_balance_tokenSell - finish_balance_tokenSell)
                                result_token_buy    = round_to(finish_balance_tokenBuy - start_balance_tokenBuy)
                                if self.token_sell == 'USDT':
                                    avg_price = round_to(result_token_sell / result_token_buy)
                                else:
                                    avg_price = round_to(result_token_buy / result_token_sell)

                                logger.success(f'{ccxt_account.name} - {account} | {result_token_sell} {self.token_sell} => {result_token_buy} {self.token_buy} | price : {avg_price}')

                            else:
                                logger.info(f"{ccxt_account.name} - {account} | order is open : {pair}")

                                # отменяем ордер
                                if self.cancel_order:
                                    try:
                                        await asyncio.sleep(self.cl_order_time)
                                        cancel_ord = await ccxt_account.cancel_order(order['id'], order['symbol'])
                                        logger.info(f"{ccxt_account.name} - {account} | order is canceled : {pair}")
                                    except Exception as error: 
                                        logger.error(f'{ccxt_account.name} - {account} | cancel order error : {error}')

                        except Exception as error:
                            logger.error(f'{ccxt_account.name} - {account} | create_order error : {error}')

                    else : 
                        logger.info(f'{ccxt_account.name} - {account} | {self.token_sell} balance {round_to(balance_of_coin)} < {self.min_sell} (min_sell)')

                else : 
                    logger.info(f'{ccxt_account.name} - {account} | current price {round_to(price_to_order)} < {self.min_price} (min_price)')

                if self.token_buy == 'USDT':
                    if self.breaker:
                        break

                else : break

            except Exception as error:
                logger.error(f'{ccxt_account.name} - {account} | error : {error}')


        await ccxt_account.close()

    async def main(self): 
        tasks = []
        for items in self.accounts:
            for account, ccxt_account in items.items():
                if (ccxt_account.name in self.exchanges and ccxt_account.name != 'OKX'):
                    cprint(f'{ccxt_account.name} - {account}', 'blue')
                    task = asyncio.create_task(self.make_trade(ccxt_account, account))
                    tasks.append(task)

        if 'OKX' in self.exchanges:
            task = asyncio.create_task(OKX().main(data_file_name=DATA_FILE_NAME,  
                                        token_sell=self.token_sell, 
                                        token_buy=self.token_buy, 
                                        amount=self.amount, 
                                        all_balance=self.all_balance, 
                                        price=self.price, 
                                        is_market_price=self.is_market_price, 
                                        spread=self.spread, 
                                        min_price=self.min_price, 
                                        breaker=self.breaker, 
                                        min_sell=self.min_sell, 
                                        cancel_order=self.cancel_order, 
                                        cl_order_time=self.cl_order_time, 
                                        module=1))
        tasks.append(task)
            
        await asyncio.gather(*tasks)
