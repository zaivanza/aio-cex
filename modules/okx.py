from .helpers import call_json, get_csv_data, round_to

from termcolor import cprint
from loguru import logger
import asyncio
import aiohttp
import hmac, base64, datetime
import datetime

def data(api_key, secret_key, passphras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):

    try:
        def signature(
            timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
        ) -> str:
            if not body:
                body = ""

            message = timestamp + method.upper() + request_path + body
            mac = hmac.new(
                bytes(secret_key, encoding="utf-8"),
                bytes(message, encoding="utf-8"),
                digestmod="sha256",
            )
            d = mac.digest()
            return base64.b64encode(d).decode("utf-8")

        dt_now = datetime.datetime.utcnow()
        ms = str(dt_now.microsecond).zfill(6)[:3]
        timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

        base_url = "https://www.okex.com"
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": passphras,
            'x-simulated-trading': '0'
        }
    except Exception as ex:
        print(ex, '--')

    return base_url, request_path, headers

async def get_balance(session, account, api_key, secret_key, passphras, token, balances):

    _, request_path, headers = data(api_key, secret_key, passphras)
    url = "https://www.okx.cab" + request_path 

    async with session.get(url, ssl=False, timeout=10, headers=headers) as resp:

        # spot balance
        _, _, headers   = data(api_key, secret_key, passphras, request_path=f"/api/v5/account/balance?ccy={token}")
        spot_balance    = await session.get(f"https://www.okx.cab/api/v5/account/balance?ccy={token}", ssl=False, timeout=10, headers=headers)
        spot_balance    = await spot_balance.json(content_type=None)

        _, _, headers   = data(api_key, secret_key, passphras, request_path=f"/api/v5/asset/balances?ccy={token}", meth="GET")
        funding_balance = await session.get(f"https://www.okx.cab/api/v5/asset/balances?ccy={token}", ssl=False, timeout=10, headers=headers) 
        funding_balance = await funding_balance.json()

        if int(spot_balance['code']) == 0:

            try:    spot_balance = float(spot_balance["data"][0]["details"][0]["cashBal"])
            except: spot_balance = 0

            try:    funding_balance = float(funding_balance["data"][0]["availBal"])
            except: funding_balance = 0

        else:

            logger.error(f"OKX - {account} | error : {spot_balance['msg']}")
            spot_balance    = 0
            funding_balance = 0

        balance = round_to(spot_balance + funding_balance)

        balances.append({'OKX':{account:balance}})

        return balances

async def trade(session, account, api_key, secret_key, passphras, proxy, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time):

    while True:

        try:

            _, request_path, headers = data(api_key, secret_key, passphras)
            url = "https://www.okx.cab" + request_path 

            async with session.get(url, ssl=False, timeout=10, headers=headers) as resp:

                if token_sell == 'USDT' : pair_ = f'{token_buy}-USDT'
                if token_buy == 'USDT'  : pair_ = f'{token_sell}-USDT'

                try:
                    # transfer from funding to spot
                    _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/asset/balances?ccy={token_sell}", meth="GET")
                    funding_balance =  await session.get(f"https://www.okx.cab/api/v5/asset/balances?ccy={token_sell}", ssl=False, timeout=10, headers=headers, proxy=proxy) 
                    funding_balance = await funding_balance.json()

                    try:
                        funding_balance = funding_balance["data"][0]["availBal"]
                    except:
                        funding_balance = 0
                    
                    if float(funding_balance) > 0:
                        body = {"ccy": token_sell, "amt": float(funding_balance), "from": 6, "to": 18, "type": "0", "subAcct": "", "clientId": "", "loanTrans": "", "omitPosRisk": ""}
                        _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/asset/transfer", body=str(body), meth="POST")
                        a = await session.post("https://www.okx.cab/api/v5/asset/transfer",data=str(body), ssl=False, timeout=10, headers=headers, proxy=proxy)
                except Exception as error: 
                    logger.error(f'OKX - {account} | transfer from funding to spot error : {error}')

                # check balance
                _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/account/balance?ccy={token_sell}")
                url = f"https://www.okx.cab/api/v5/account/balance?ccy={token_sell}"
                check_balance =  await session.get(url, ssl=False, timeout=10, headers=headers, proxy=proxy)
                check_balance = await check_balance.json(content_type=None)

                if int(check_balance['code']) == 0:

                    try:
                        balance_of_coin = round_to(float(check_balance["data"][0]["details"][0]["cashBal"]))
                    except:
                        balance_of_coin = 0

                    logger.info(f'OKX - {account} | balance of {token_sell} : {balance_of_coin}')

                
                    try:

                        if is_market_price == True:

                            order_book = await session.get(f"https://www.okx.cab/api/v5/market/books?instId={pair_}", ssl=False, timeout=10, proxy=proxy)
                            order_book = await order_book.json(content_type=None)

                            order_bids = order_book["data"][0]['bids'][0][0]
                            order_asks = order_book["data"][0]['asks'][0][0]

                            if token_sell == 'USDT': price_to_order = float(order_asks) + float(order_asks) * (spread/100)
                            if token_buy == 'USDT': price_to_order = float(order_bids) - float(order_bids) * (spread/100)

                        else: price_to_order = price


                        if all_balance == True: 
                            amount = balance_of_coin * 0.9999 # умножаем на 0.9999 чтобы не было проблем с балансом и точно свапнулось
                        else:
                            amount = amount


                        if balance_of_coin > 0:
                            if balance_of_coin >= min_sell:

                                if float(price_to_order) >= min_price:

                                    if token_sell == 'USDT':
                                        
                                        body = {"instId": pair_, "tdMode": "cash", "side": "buy", "ordType": "limit", "sz": float(amount)/float(price_to_order), "ccy": "", "clOrdId": "b15", "tag": "", "posSide": "", "px": float(price_to_order), "reduceOnly": "", "tgtCcy": "", "banAmend": ""}
                                        _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/trade/order", body=str(body), meth="POST")
                                        order = await session.post("https://www.okx.cab/api/v5/trade/order",data=str(body), ssl=False, timeout=10, headers=headers, proxy=proxy)
                                        order = await order.json(content_type=None)

                                    elif token_buy == 'USDT':
                                        
                                        body = {"instId": pair_, "tdMode": "cash", "side": "sell", "ordType": "limit", "sz": float(amount), "ccy": "", "clOrdId": "b15", "tag": "", "posSide": "", "px": float(price_to_order), "reduceOnly": "", "tgtCcy": "", "banAmend": ""}
                                        _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/trade/order", body=str(body), meth="POST")
                                        order = await session.post("https://www.okx.cab/api/v5/trade/order",data=str(body), ssl=False, timeout=10, headers=headers, proxy=proxy)
                                        order = await order.json(content_type=None)

                                else : 
                                    logger.info(f'OKX - {account} | current price {round_to(price_to_order)} < {min_price} (min_price)')

                            else:
                                logger.info(f'OKX - {account} | {token_sell} balance {round_to(balance_of_coin)} < {min_sell} (min_sell)')


                    except Exception as error:
                        logger.error(f'OKX - {account} | error : {error}')
                        return ''

                    if balance_of_coin > 0:

                        if (balance_of_coin >= min_sell and float(price_to_order) >= min_price):

                            if int(order['code']) == 0:

                                try:
                                    # смотрим статус ордера
                                    await asyncio.sleep(3)
                                    order_id = int(order['data'][0]['ordId'])
                                    _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/trade/order?ordId={order_id}&instId={pair_}")
                                    order_status = await session.get(f"https://www.okx.cab/api/v5/trade/order?ordId={order_id}&instId={pair_}", ssl=False, timeout=10, headers=headers)
                                    order_status = await order_status.json(content_type=None)

                                    order_filled_size  = float(order_status['data'][0]['accFillSz']) # на сколько заполнен ордер

                                except Exception as error:
                                    logger.error(error)
                                    order_filled_size = 0

                                try:
                                    if order_filled_size > 0:

                                        order_avg_price     = float(order_status['data'][0]['avgPx']) # средняя цена заполнения ордера
                                        order_size          = float(order_status['data'][0]['accFillSz']) # сколько монет (не usdt) мы отдали / получили 
                                        filled_get_size     = round_to(order_avg_price * order_size) # сколько token_buy мы получили

                                        if token_sell == 'USDT':
                                            logger.success(f'OKX - {account} | {round_to(filled_get_size)} {token_sell} => {round_to(order_size)} {token_buy} | price : {round_to(order_avg_price)}')
                                        if token_buy == 'USDT':
                                            logger.success(f'OKX - {account} | {round_to(order_size)} {token_sell} => {round_to(filled_get_size)} {token_buy} | price : {round_to(order_avg_price)}')

                                    else:

                                        try:
                                            # отменяем ордер
                                            if cancel_order == True:
                        
                                                logger.info(f"OKX - {account} | order is open : {pair_}")
                                                await asyncio.sleep(cl_order_time)
                                                
                                                body = {"instId": pair_, "clOrdId": "b15", "ordId": order_id}
                                                _, _, headers = data(api_key, secret_key, passphras, request_path=f"/api/v5/trade/cancel-order", body=str(body), meth="POST")
                                                canceled = await session.post("https://www.okx.cab/api/v5/trade/cancel-order",data=str(body), ssl=False, timeout=10, headers=headers)
                                                canceled = await canceled.json(content_type=None)

                                                if int(canceled['code']) == 0:
                                                    logger.info(f"OKX - {account} | order is canceled : {pair_}")
                                                else:
                                                    logger.info(f"OKX - {account} | cancel error : {canceled['data'][0]['sMsg']}")

                                        except Exception as error:
                                            logger.error(error)  

                                    
                                except Exception as error:
                                    logger.error(error)

                            elif int(order['code']) == 1:
                                logger.error(f'OKX - {account} | cant make order. error : {order["data"][0]["sMsg"]}')
                            else:
                                logger.error(f'OKX - {account} | cant make order. error : {order["msg"]}')

                else:
                    logger.error(f'OKX - {account} | error : {check_balance["msg"]}')

            
            if token_buy == 'USDT':
                if breaker == True:
                    return ''
            else :  return ''


        except Exception as error:
            logger.error(f'OKX - {account} | error : {error}')
            await asyncio.sleep(3)

async def main(data_file_name='', token_sell='', token_buy='', amount='', all_balance='', price='', is_market_price='', spread='', min_price='', breaker='', min_sell='', cancel_order='', cl_order_time='', module='', balance_token='', balances=''):

    exchanges_data = get_csv_data(data_file_name)

    async with aiohttp.ClientSession() as session:

        tasks = []

        for data in exchanges_data:

            exchange    = data['exchange']
            account     = data['account']
            api_key     = data['api_key']
            api_secret  = data['api_secret']
            password    = data['password']
            proxy       = data['proxy']

            if exchange == 'okx':

                cprint(f'OKX - {account}', 'blue')

                if module == 0:
                    task = asyncio.create_task(get_balance(session, account, api_key, api_secret, password, balance_token, balances))
                if module == 1:
                    task = asyncio.create_task(trade(session, account, api_key, api_secret, password, proxy, token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time))

                tasks.append(task)

        await asyncio.gather(*tasks)

        if module == 0:
            return balances
    



