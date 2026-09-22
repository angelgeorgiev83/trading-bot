import time
import requests
from datetime import datetime

def get_crypto_price(symbol="BTCUSDT"):
    """Извлича цена на криптовалута от Binance"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Грешка при крипто: {e}")
        return None

def get_stock_or_forex_price(symbol="AAPL"):
    """Извлича цена на акция или злато (GC=F за XAU/USD) от Yahoo Finance API"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return float(price)
    except Exception as e:
        print(f"Грешка при извличане на цена за {symbol}: {e}")
        return None

def log_trade(message):
    """Записва сделка във външен файл с дата и час"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open("trading_log.txt", "a", encoding="utf-8") as file:
        file.write(log_line)

# --- НАЧАЛНИ ПАРАМЕТРИ ---
balance = 10000.0

# 1. Биткойн (BTC)
btc_holdings = 0.0
btc_buy_price = 0.0
btc_last_price = None

# 2. Злато (XAU/USD)
gold_holdings = 0.0
gold_buy_price = 0.0
gold_last_price = None

# 3. Акции Apple (AAPL)
aapl_holdings = 0
aapl_buy_price = 0.0
aapl_last_price = None

check_count = 0

log_trade("=== СТАРТИРАНЕ НА TRADING БОТ (BTC, XAU/USD, AAPL) ===")
log_trade(f"Начален баланс: ${balance:.2f}")

try:
    while True:
        check_count += 1
        print(f"\n--- Проверка #{check_count} ---")
        
        # 1. СЛЕДЕНЕ НА БИТКОЙН
        btc_price = get_crypto_price("BTCUSDT")
        if btc_price:
            print(f"BTC цена:      ${btc_price:,.2f}")
            if btc_last_price is None:
                btc_last_price = btc_price
            else:
                if btc_holdings == 0 and btc_price <= (btc_last_price - 3.0):
                    cost = 0.05 * btc_price
                    if balance >= cost:
                        balance -= cost
                        btc_holdings = 0.05
                        btc_buy_price = btc_price
                        log_trade(f"[BTC ПОКУПКА] 0.05 BTC на ${btc_price:,.2f} | Баланс: ${balance:,.2f}")
                elif btc_holdings > 0 and btc_price >= (btc_buy_price + 3.0):
                    revenue = btc_holdings * btc_price
                    profit = revenue - (btc_holdings * btc_buy_price)
                    balance += revenue
                    log_trade(f"[BTC ПРОДАЖБА] 0.05 BTC на ${btc_price:,.2f} | Печалба: +${profit:,.2f} | Нов баланс: ${balance:,.2f}")
                    btc_holdings = 0.0
                    btc_buy_price = 0.0
                    btc_last_price = btc_price

        # 2. СЛЕДЕНЕ НА ЗЛАТО (XAU/USD)
        gold_price = get_stock_or_forex_price("GC=F")
        if gold_price:
            print(f"XAU/USD цена:  ${gold_price:,.2f} / oz")
            if gold_last_price is None:
                gold_last_price = gold_price
            else:
                if gold_holdings == 0 and gold_price <= (gold_last_price - 1.50):
                    cost = 0.1 * gold_price
                    if balance >= cost:
                        balance -= cost
                        gold_holdings = 0.1
                        gold_buy_price = gold_price
                        log_trade(f"[XAU/USD ПОКУПКА] 0.1 oz на ${gold_price:,.2f} | Баланс: ${balance:,.2f}")
                elif gold_holdings > 0 and gold_price >= (gold_buy_price + 1.50):
                    revenue = gold_holdings * gold_price
                    profit = revenue - (gold_holdings * gold_buy_price)
                    balance += revenue
                    log_trade(f"[XAU/USD ПРОДАЖБА] 0.1 oz на ${gold_price:,.2f} | Печалба: +${profit:,.2f} | Нов баланс: ${balance:,.2f}")
                    gold_holdings = 0.0
                    gold_buy_price = 0.0
                    gold_last_price = gold_price

        # 3. СЛЕДЕНЕ НА APPLE
        aapl_price = get_stock_or_forex_price("AAPL")
        if aapl_price:
            print(f"AAPL цена:     ${aapl_price:,.2f}")
            if aapl_last_price is None:
                aapl_last_price = aapl_price
            else:
                if aapl_holdings == 0 and aapl_price <= (aapl_last_price - 0.20):
                    cost = 5 * aapl_price
                    if balance >= cost:
                        balance -= cost
                        aapl_holdings = 5
                        aapl_buy_price = aapl_price
                        log_trade(f"[AAPL ПОКУПКА] 5 акции на ${aapl_price:,.2f} | Баланс: ${balance:,.2f}")
                elif aapl_holdings > 0 and aapl_price >= (aapl_buy_price + 0.20):
                    revenue = aapl_holdings * aapl_price
                    profit = revenue - (aapl_holdings * aapl_buy_price)
                    balance += revenue
                    log_trade(f"[AAPL ПРОДАЖБА] 5 акции на ${aapl_price:,.2f} | Печалба: +${profit:,.2f} | Нов баланс: ${balance:,.2f}")
                    aapl_holdings = 0
                    aapl_buy_price = 0.0
                    aapl_last_price = aapl_price

        time.sleep(3)

except KeyboardInterrupt:
    log_trade("=== БОТЪТ БЕШЕ СПРЯН РЪЧНО ===")
    log_trade(f"Краен баланс: ${balance:,.2f}")