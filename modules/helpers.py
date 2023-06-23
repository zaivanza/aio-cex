import time
import json
import random
import csv
import ccxt.async_support as ccxt
import math
from tqdm import tqdm

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def round_to(num, digits=3):
    try:
        if num == 0: return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def get_csv_data(data_file_name):
    '''получаем данные по биржам из csv файла'''

    data = []
    with open(data_file_name, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader: data.append(row)

    return data

def get_account(exchange, account, api_key, api_secret, password, proxy):

    headers = {
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    }

    if password not in ['', ' ']:
        headers['password'] = password

    if proxy not in ['', ' ']:
        headers['proxies'] = {
            'http': proxy,  
            'https': proxy,  
        }

    ccxt_account = ccxt.__dict__[exchange](headers)

    return ccxt_account

def get_ccxt_accounts(data_file_name):

    exchanges_data = get_csv_data(data_file_name)

    accounts = []
    for data in exchanges_data:

        exchange    = data['exchange']
        account     = data['account']
        api_key     = data['api_key']
        api_secret  = data['api_secret']
        password    = data['password']
        proxy       = data['proxy']

        ccxt_account = get_account(exchange, account, api_key, api_secret, password, proxy)
        accounts.append({account:ccxt_account})

    return accounts

text1 = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$      /$$  /$$$$$$  /$$$$$$$ 
| $$  | $$ /$$__  $$| $$__  $$| $$      | $$$    /$$$ /$$__  $$| $$__  $$
| $$  | $$| $$  \ $$| $$  \ $$| $$      | $$$$  /$$$$| $$  \ $$| $$  \ $$
| $$$$$$$$| $$  | $$| $$  | $$| $$      | $$ $$/$$ $$| $$  | $$| $$  | $$
| $$__  $$| $$  | $$| $$  | $$| $$      | $$  $$$| $$| $$  | $$| $$  | $$
| $$  | $$| $$  | $$| $$  | $$| $$      | $$\  $ | $$| $$  | $$| $$  | $$
| $$  | $$|  $$$$$$/| $$$$$$$/| $$$$$$$$| $$ \/  | $$|  $$$$$$/| $$$$$$$/
|__/  |__/ \______/ |_______/ |________/|__/     |__/ \______/ |_______/                                                                                                                                                                                                          
'''

text2 = '''
      ___          ___                                    ___          ___                  
     /\  \        /\  \        _____                     /\  \        /\  \        _____    
     \:\  \      /::\  \      /::\  \                   |::\  \      /::\  \      /::\  \   
      \:\  \    /:/\:\  \    /:/\:\  \                  |:|:\  \    /:/\:\  \    /:/\:\  \  
  ___ /::\  \  /:/  \:\  \  /:/  \:\__\  ___     ___  __|:|\:\  \  /:/  \:\  \  /:/  \:\__\ 
 /\  /:/\:\__\/:/__/ \:\__\/:/__/ \:|__|/\  \   /\__\/::::|_\:\__\/:/__/ \:\__\/:/__/ \:|__|
 \:\/:/  \/__/\:\  \ /:/  /\:\  \ /:/  /\:\  \ /:/  /\:\~~\  \/__/\:\  \ /:/  /\:\  \ /:/  /
  \::/__/      \:\  /:/  /  \:\  /:/  /  \:\  /:/  /  \:\  \       \:\  /:/  /  \:\  /:/  / 
   \:\  \       \:\/:/  /    \:\/:/  /    \:\/:/  /    \:\  \       \:\/:/  /    \:\/:/  /  
    \:\__\       \::/  /      \::/  /      \::/  /      \:\__\       \::/  /      \::/  /   
     \/__/        \/__/        \/__/        \/__/        \/__/        \/__/        \/__/    
'''

texts = [text1, text2]
colors = ['green', 'blue', 'magenta', 'cyan']

RUN_TEXT    = random.choice(texts)
RUN_COLOR   = random.choice(colors)


