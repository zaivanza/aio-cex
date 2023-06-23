
# с какими биржами работаем. закомментируй, если хочешь отключить биржу
EXCHANGES = [
    "Binance", 
    "KuCoin", 
    "Bybit", 
    "Huobi",
    "OKX",
]

# путь к файлу с данными от бирж
DATA_FILE_NAME = 'data.csv' 

def value_get_balance(): 

    token = 'USDT' # баланс какого токена хочешь получить

    return token
    
def value_trade():

    token_sell      = 'ARB' # какой токен продаем
    token_buy       = 'USDT' # какой токен покупаем

    amount          = 15 # сколько продаем token_sell, чтобы купить token_buy
    all_balance     = True # True / False. True если хочешь продать все монеты token_sell. если False, тогда берется значение amount

    price           = 1.05 # какую цену ставим. 
    is_market_price = True # True / False. True если покупаем / продаем по маркету, False если берем цену из price
    spread          = 1 # на какой процент цена будет отличаться от маркета (выше / ниже в зависимости от TYPE_SIDE)
    min_price       = 1 # если цена ниже этой, продавать не будет

    breaker         = False # True / False. True если хочешь пройтись по аккаунтам 1 раз, False если хочешь смотреть баланс и продавать бесконечно. При token_buy = USDT, режим breaker всегда = False

    min_sell        = 5 # если кол-во token_sell будет меньше этого числа, свап не произойдет. советую ставить > 0
    cancel_order    = True # True / False. если True, тогда после не имполнении ордера, он будет отменен. нужно при большой волатильности
    cl_order_time   = 3 # через сколько секунд ордер будет отменен (3 = дефолт)

    return token_sell, token_buy, amount, all_balance, price, is_market_price, spread, min_price, breaker, min_sell, cancel_order, cl_order_time

