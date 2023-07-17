
# с какими биржами работаем. закомментируй, если хочешь отключить биржу
EXCHANGES = [
    "Binance", 
    "KuCoin", 
    "Bybit", 
    # "Huobi",
    "OKX",
]

# путь к файлу с данными от бирж
DATA_FILE_NAME = 'data.csv' 

def value_get_balance(): 

    token   = 'USDT' # баланс какого токена хочешь получить
    account = 'spot' # funding / spot

    return token, account
    
def value_trade():

    token_sell      = 'MNT' # какой токен продаем
    token_buy       = 'USDT' # какой токен покупаем

    amount          = 199 # сколько продаем token_sell, чтобы купить token_buy
    all_balance     = True # True / False. True если хочешь продать все монеты token_sell. если False, тогда берется значение amount

    price           = 0.3 # какую цену ставим (работает при is_market_price = False)
    is_market_price = True # True / False. True если покупаем / продаем по маркету, False если берем цену из price
    spread          = 5 # на какой процент цена будет отличаться от маркета (работает при is_market_price = True)
    min_price       = 0.1 # если цена ниже этой, продавать не будет

    breaker         = False # True / False. True если хочешь пройтись по аккаунтам 1 раз, False если хочешь смотреть баланс и продавать бесконечно. При token_sell = USDT, режим breaker всегда = True

    min_sell        = 10 # если кол-во token_sell будет меньше этого числа, свап не произойдет. советую ставить > 0
    cancel_order    = True # True / False. если True, тогда при не исполнении ордера, он будет отменен через cl_order_time секунд. нужно при большой волатильности
    cl_order_time   = 3 # через сколько секунд ордер будет отменен (3 = дефолт)

    return token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time

def value_transfer(): 

    '''
    трансфер с фандинга на спот или наоборот.
    доступные биржи (позже остальные добавлю) : Bybit 
    не забудь отключить остальные биржи в EXCHANGES.
    '''

    token           = 'MNT' # какой токен хочешь сделать трансфер
    from_account    = 'funding'
    to_account      = 'spot'

    return token, from_account, to_account

