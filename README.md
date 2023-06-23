[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=AIO-cex)](https://git.io/typing-svg)

Скрипт по работе с биржами binance, okx, bybit, kucoin, huobi. Есть 2 модуля :
1. get balance : проверяет баланс определенной монеты на всех биржах, вывод результата в терминал и csv файл.
2. make trade : делает трейд по заданным настройкам.

## Подготовка :

Создаем виртуальное окружение :
`python3 -m venv .venv`

Активируем :
`.venv\Scripts\activate.bat` or `.venv\Scripts\activate.ps1` - для Windows.
`source .venv/bin/activate` - для Linux и MacOS.

Устанавливаем библиотеки :
`pip install -r requirements.txt`

## Настройка `data.csv` :

В гугл / эксель таблицу нужно выписать данные от биржи, скачать как csv файл и поместить этот файл в папку. Для наглядности я оставил файл `data.csv`. Образец гугл таблицы : https://docs.google.com/spreadsheets/d/1_-RXkzyQmmN-sZqODaqTqyRoM5Bjq7S_URCLzlukU2o/edit?usp=sharing. Создаешь свою таблицу на основе этой таблицы и меняешь значения на свои.
   - exchange : название биржи (binance / okx / bybit / huobi / kucoin).
   - account : любое название аккаунта, сделано для удобства.
   - api_key : api key от аккаунта.
   - api_secret : api secret от аккаунта.
   - api_key : api password от аккаунта, нужен для kucoin и okx. для остальных бирж оставляй пустое поле.
   - proxy : по желанию. если оставить пустое поле, то будет работать без прокси. формат : http://login:password@ip:port
     
## Настройка `setting.py` :
- `EXCHANGES` : с какими биржами будешь работать. закомментируй биржу чтобы отключить ее.
- `DATA_FILE_NAME` : путь к файлу с данными от биржи. по дефолту `data.csv`.
- функция value_get_balance : описание значений внутри функции.
- функция value_trade : описание значений внутри функции. В OKX автоматически идет перевод средств с funding на spot. На других биржах это (пока что) не реализовано.

Важно! На некоторых биржах чтобы работать через апи ключ, нужно привязать свой ip адрес. Если будешь работать с биржей-аккаунтом через прокси, не забудь добавить этот прокси в IP апи ключа. Также большая просьба сначала все потыкать самому, поизучать как все работает, запустить скрипт раз 30, и только потом задавать вопросы в чат.

Паблик : https://t.me/hodlmodeth. [ code ] чат : https://t.me/code_hodlmodeth
