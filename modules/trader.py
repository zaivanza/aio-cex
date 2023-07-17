from termcolor import cprint
import asyncio
import ccxt.async_support as ccxt
from loguru import logger
from .helpers import round_to, get_ccxt_accounts
from .okx import main as okx

async def trade(ccxt_account, account, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time):

    while True:
            
        try:

            # смотрим изначальный баланс для просчета разницы (профита)
            check_balance = await ccxt_account.fetch_balance()
            try:        start_balance_tokenSell = check_balance[token_sell]['free']
            except :    start_balance_tokenSell = 0
            try:        start_balance_tokenBuy  = check_balance[token_buy]['free']
            except :    start_balance_tokenBuy  = 0

            if token_sell == 'USDT' : pair = f'{token_buy}/USDT'
            if token_buy == 'USDT'  : pair = f'{token_sell}/USDT'

            # check balance
            check_balance   = await ccxt_account.fetch_balance()
            try:    balance_of_coin = round_to(check_balance[token_sell]['free'])
            except: balance_of_coin = 0
            logger.info(f'{ccxt_account.name} - {account} | balance of {token_sell} : {balance_of_coin}')

            if is_market_price == True:
                while True:
                    try:
                        # check book of pair 
                        order_book = await ccxt_account.fetch_order_book(pair)
                        order_bids = order_book['bids'][0][0]
                        order_asks = order_book['asks'][0][0]

                        if token_sell == 'USDT' : price_to_order = order_asks + order_asks * (spread / 100)
                        elif token_buy == 'USDT': price_to_order = order_bids - order_bids * (spread / 100)
                        break
                    except Exception as error:
                        logger.error(f'{ccxt_account.name} - {account} | ckeck_price error : {error}')
                        await asyncio.sleep(0.5)

            else : price_to_order = price

            if price_to_order >= min_price:
                
                if balance_of_coin >= min_sell:

                    try:

                        if all_balance == True:
                            amount = balance_of_coin * 0.9999 # умножаем на 0.9999 тк может возникнуть ошибка с балансом

                        # make order
                        if token_sell == 'USDT':

                            order = await ccxt_account.create_limit_buy_order(
                                symbol = pair,
                                amount = amount / price_to_order,
                                price  = price_to_order,
                                params = {}
                            )

                        elif token_buy == 'USDT':

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
                            try:        finish_balance_tokenSell = check_balance[token_sell]['free']
                            except :    finish_balance_tokenSell = 0
                            try:        finish_balance_tokenBuy  = check_balance[token_buy]['free']
                            except :    finish_balance_tokenBuy  = 0

                            result_token_sell   = round_to(start_balance_tokenSell - finish_balance_tokenSell)
                            result_token_buy    = round_to(finish_balance_tokenBuy - start_balance_tokenBuy)
                            if token_sell == 'USDT':
                                avg_price = round_to(result_token_sell / result_token_buy)
                            else:
                                avg_price = round_to(result_token_buy / result_token_sell)

                            logger.success(f'{ccxt_account.name} - {account} | {result_token_sell} {token_sell} => {result_token_buy} {token_buy} | price : {avg_price}')

                        else:
                            logger.info(f"{ccxt_account.name} - {account} | order is open : {pair}")

                            # отменяем ордер
                            if cancel_order == True:
                                try:
                                    await asyncio.sleep(cl_order_time)
                                    cancel_ord = await ccxt_account.cancel_order(order['id'], order['symbol'])
                                    logger.info(f"{ccxt_account.name} - {account} | order is canceled : {pair}")
                                except Exception as error: 
                                    logger.error(f'{ccxt_account.name} - {account} | cancel order error : {error}')

                    except Exception as error:
                        logger.error(f'{ccxt_account.name} - {account} | create_order error : {error}')

                else : 
                    logger.info(f'{ccxt_account.name} - {account} | {token_sell} balance {round_to(balance_of_coin)} < {min_sell} (min_sell)')

            else : 
                logger.info(f'{ccxt_account.name} - {account} | current price {round_to(price_to_order)} < {min_price} (min_price)')

            if token_buy == 'USDT':
                if breaker == True:
                    break

            else : break

        except Exception as error:
            logger.error(f'{ccxt_account.name} - {account} | error : {error}')


    await ccxt_account.close()

async def main(data_file_name, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time, exchanges): 

    accounts = get_ccxt_accounts(data_file_name)

    tasks = []

    for items in accounts:
        for item in items.items():

            account = item[0]
            ccxt_account = item[1]

            if (ccxt_account.name in exchanges and ccxt_account.name != 'OKX'):
                cprint(f'{ccxt_account.name} - {account}', 'blue')
                task = asyncio.create_task(trade(ccxt_account, account, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time))
                tasks.append(task)

    if 'OKX' in exchanges:
        task = asyncio.create_task(okx(data_file_name=data_file_name,  
                                    token_sell=token_sell, 
                                    token_buy=token_buy, 
                                    amount=amount, 
                                    all_balance=all_balance, 
                                    price=price, 
                                    is_market_price=is_market_price, 
                                    spread=spread, 
                                    min_price=min_price, 
                                    breaker=breaker, 
                                    min_sell=min_sell, 
                                    cancel_order=cancel_order, 
                                    cl_order_time=cl_order_time, 
                                    module=1))
    tasks.append(task)
        
    await asyncio.gather(*tasks)


