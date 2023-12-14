
# C какими биржами работаем. Закомментируй биржу, если хочешь ее отключить.
EXCHANGES = [
    # "Binance", 
    # "KuCoin", 
    "Bybit", 
    # "Huobi",
    # "OKX",
]

# Путь к файлу с данными от бирж.
DATA_FILE_NAME = 'data.csv' 

class ValueGetBalance: 

    """
    Просмотр баланса монеты.
    Доступные биржи: Bybit, Binance, KuCoin, Huobi, OKX.
    """

    token   = 'USDT' # баланс какого токена хочешь получить
    account = 'funding' # funding / spot
    
class ValueTrade:

    """
    Покупка/продажа монеты.
    Доступные биржи: Bybit, Binance, KuCoin, Huobi, OKX.
    """

    token_sell      = '5IRE' # какой токен продаем
    token_buy       = 'USDT' # какой токен покупаем

    amount          = 0 # сколько продаем token_sell, чтобы купить token_buy
    all_balance     = True # True / False. True если хочешь продать все монеты token_sell. если False, тогда берется значение amount

    price           = 0.2 # какую цену ставим (работает при is_market_price = False)
    is_market_price = True # True / False. True если покупаем / продаем по маркету, False если берем цену из price
    spread          = 3 # на какой процент цена будет отличаться от маркета (работает при is_market_price = True)
    min_price       = 0.1 # если цена ниже этой, продавать не будет

    breaker         = False # True / False. True если хочешь пройтись по аккаунтам 1 раз, False если хочешь смотреть баланс и продавать бесконечно. При token_sell = USDT, режим breaker всегда = True

    min_sell        = 1 # если кол-во token_sell будет меньше этого числа, свап не произойдет. советую ставить > 0
    cancel_order    = True # True / False. если True, тогда при не исполнении ордера, он будет отменен через cl_order_time секунд. нужно при большой волатильности
    cl_order_time   = 3 # через сколько секунд ордер будет отменен (3 = дефолт)

class ValueTransfer: 

    '''
    Трансфер с фандинга на спот или наоборот.
    Доступные биржи: Bybit.
    Не забудь отключить остальные биржи в EXCHANGES.
    '''

    token           = 'USDT' # какой токен хочешь сделать трансфер
    from_account    = 'funding' # funding / spot
    to_account      = 'spot' # funding / spot

class ValueWithdraw:

    '''
    Вывод монеты с биржи на один адрес.
    Доступные биржи: Bybit, Binance, KuCoin, Huobi.
    Не забудь отключить остальные биржи в EXCHANGES.
    '''

    symbol = "USDT" # какую монету выводим
    chain = "BEP20" # в какой сети монету выводим
    amounts = [0, 0] # от скольки до скольки выводим
    withdraw_all_balance = True # True если хочешь вывести весь баланс, False если смотрим на amounts
    fee = 0.5 # ставь с небольшим запасом, если 0.3, то ставь > 0.3
    min_withdraw = 3 # если баланс меньше этого значения, выводить не будет с аккаунта не будет

    recipient = "0x_your_address_wallet" # получатель, куда все выводим
