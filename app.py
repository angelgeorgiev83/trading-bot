import streamlit as st
import requests
import os
import csv
from datetime import datetime

# Настройка на страницата
st.set_page_config(page_title="Trading Bot Pro", page_icon="📈", layout="wide")

# --- ФАЙЛ ЗА ИСТОРИЯ НА СДЕЛКИТЕ ---
CSV_FILE = "trades.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Час", "Актив", "Тип", "Количество", "Цена", "Сума USD", "Баланс"])

def save_trade_to_csv(trade):
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([trade["Час"], trade["Актив"], trade["Тип"], trade["Количество"], trade["Цена"], trade["Сума USD"], trade["Баланс"]])

def clear_csv():
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Час", "Актив", "Тип", "Количество", "Цена", "Сума USD", "Баланс"])

init_csv()

# --- ФУНКЦИИ ЗА ИЗВЛИЧАНЕ НА ЦЕНИ ---
def get_crypto_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        return float(response.json()['price'])
    except:
        return None

def get_stock_or_forex_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return float(response.json()['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return None

# --- ИНИЦИАЛИЗАЦИЯ НА СЪСТОЯНИЕТО ---
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
    st.session_state.trades = []
    st.session_state.balance_history = [10000.0]
    
    st.session_state.btc_holdings = 0.0
    st.session_state.btc_buy_price = 0.0
    st.session_state.btc_last_price = None

    st.session_state.gold_holdings = 0.0
    st.session_state.gold_buy_price = 0.0
    st.session_state.gold_last_price = None

    st.session_state.aapl_holdings = 0.0
    st.session_state.aapl_buy_price = 0.0
    st.session_state.aapl_last_price = None

# --- СТРАНИЧЕН ПАНЕЛ (SIDEBAR) ---
st.sidebar.title("⚙️ Настройки на Бота")

st.sidebar.subheader("🎯 Прагове за авто-търговия")
btc_trigger = st.sidebar.slider("BTC Праг ($)", min_value=1.0, max_value=50.0, value=3.0, step=1.0)
gold_trigger = st.sidebar.slider("Gold Праг ($)", min_value=0.5, max_value=10.0, value=1.5, step=0.5)
aapl_trigger = st.sidebar.slider("AAPL Праг ($)", min_value=0.1, max_value=5.0, value=0.2, step=0.1)

st.sidebar.divider()
if st.sidebar.button("🔄 Нулиране на сметката ($10,000)"):
    st.session_state.balance = 10000.0
    st.session_state.trades = []
    st.session_state.balance_history = [10000.0]
    st.session_state.btc_holdings = 0.0
    st.session_state.gold_holdings = 0.0
    st.session_state.aapl_holdings = 0.0
    clear_csv()
    st.sidebar.success("Сметката беше нулирана!")

# --- ОСНОВЕН ИНТЕРФЕЙС ---
st.title("📈 Автоматичен & Ръчен Trading Бот")
st.write("Контролирай сумите при покупка, следи пазарните цени и реалния PnL.")

# Извличане на цените на живо
btc_p = get_crypto_price("BTCUSDT")
gold_p = get_stock_or_forex_price("GC=F")
aapl_p = get_stock_or_forex_price("AAPL")

# Изчисляване на PnL и стойност на позициите
btc_val = st.session_state.btc_holdings * (btc_p if btc_p else st.session_state.btc_buy_price)
btc_pnl = st.session_state.btc_holdings * ((btc_p - st.session_state.btc_buy_price) if btc_p and st.session_state.btc_buy_price > 0 else 0)

gold_val = st.session_state.gold_holdings * (gold_p if gold_p else st.session_state.gold_buy_price)
gold_pnl = st.session_state.gold_holdings * ((gold_p - st.session_state.gold_buy_price) if gold_p and st.session_state.gold_buy_price > 0 else 0)

aapl_val = st.session_state.aapl_holdings * (aapl_p if aapl_p else st.session_state.aapl_buy_price)
aapl_pnl = st.session_state.aapl_holdings * ((aapl_p - st.session_state.aapl_buy_price) if aapl_p and st.session_state.aapl_buy_price > 0 else 0)

total_portfolio_value = st.session_state.balance + btc_val + gold_val + aapl_val
total_pnl = total_portfolio_value - 10000.0

# Картички с основни показатели
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Свободен баланс", f"${st.session_state.balance:,.2f}")
col2.metric("📊 Портфейл общо", f"${total_portfolio_value:,.2f}")
col3.metric("📈 Общ PnL ($)", f"${total_pnl:,.2f}", delta=f"${total_pnl:,.2f}")
col4.metric("₿ BTC Цена", f"${btc_p:,.2f}" if btc_p else "---")
col5.metric("🥇 Gold Цена", f"${gold_p:,.2f}" if gold_p else "---")

st.divider()

# --- ПАНЕЛ ЗА ПЕЧАЛБА/ЗАГУБА ПО АКТИВИ ---
st.subheader("📌 Текущи позиции и PnL")
pos_c1, pos_c2, pos_c3 = st.columns(3)
with pos_c1:
    st.info(f"**BTC позиция**: {st.session_state.btc_holdings:,.6f} BTC\n\nКупена на: ${st.session_state.btc_buy_price:,.2f}\n\n**PnL**: ${btc_pnl:,.2f}")
with pos_c2:
    st.info(f"**Gold позиция**: {st.session_state.gold_holdings:,.4f} oz\n\nКупена на: ${st.session_state.gold_buy_price:,.2f}\n\n**PnL**: ${gold_pnl:,.2f}")
with pos_c3:
    st.info(f"**AAPL позиция**: {st.session_state.aapl_holdings:,.2f} акции\n\nКупена на: ${st.session_state.aapl_buy_price:,.2f}\n\n**PnL**: ${aapl_pnl:,.2f}")

st.divider()

# --- АВТОМАТИЧНА ЛОГИКА ---
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def record_trade(asset, trade_type, qty, price, usd_amount):
    trade_info = {
        "Час": now_str,
        "Актив": asset,
        "Тип": trade_type,
        "Количество": f"{qty:,.6f}" if "BTC" in asset or "oz" in asset else f"{qty:,.2f}",
        "Цена": f"${price:,.2f}",
        "Сума USD": f"${usd_amount:,.2f}",
        "Баланс": f"${st.session_state.balance:,.2f}"
    }
    st.session_state.trades.append(trade_info)
    st.session_state.balance_history.append(total_portfolio_value)
    save_trade_to_csv(trade_info)

# 1. BTC авто
if btc_p:
    if st.session_state.btc_last_price is None:
        st.session_state.btc_last_price = btc_p
    else:
        if st.session_state.btc_holdings == 0 and btc_p <= (st.session_state.btc_last_price - btc_trigger):
            cost = 0.05 * btc_p
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                qty = 0.05
                st.session_state.btc_holdings = qty
                st.session_state.btc_buy_price = btc_p
                record_trade("BTC", "ПОКУПКА (АВТО)", qty, btc_p, cost)
        elif st.session_state.btc_holdings > 0 and btc_p >= (st.session_state.btc_buy_price + btc_trigger):
            revenue = st.session_state.btc_holdings * btc_p
            st.session_state.balance += revenue
            record_trade("BTC", "ПРОДАЖБА (АВТО)", st.session_state.btc_holdings, btc_p, revenue)
            st.session_state.btc_holdings = 0.0
            st.session_state.btc_buy_price = 0.0
            st.session_state.btc_last_price = btc_p

# 2. Gold авто
if gold_p:
    if st.session_state.gold_last_price is None:
        st.session_state.gold_last_price = gold_p
    else:
        if st.session_state.gold_holdings == 0 and gold_p <= (st.session_state.gold_last_price - gold_trigger):
            cost = 0.1 * gold_p
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                qty = 0.1
                st.session_state.gold_holdings = qty
                st.session_state.gold_buy_price = gold_p
                record_trade("XAU/USD", "ПОКУПКА (АВТО)", qty, gold_p, cost)
        elif st.session_state.gold_holdings > 0 and gold_p >= (st.session_state.gold_buy_price + gold_trigger):
            revenue = st.session_state.gold_holdings * gold_p
            st.session_state.balance += revenue
            record_trade("XAU/USD", "ПРОДАЖБА (АВТО)", st.session_state.gold_holdings, gold_p, revenue)
            st.session_state.gold_holdings = 0.0
            st.session_state.gold_buy_price = 0.0
            st.session_state.gold_last_price = gold_p

# 3. AAPL авто
if aapl_p:
    if st.session_state.aapl_last_price is None:
        st.session_state.aapl_last_price = aapl_p
    else:
        if st.session_state.aapl_holdings == 0 and aapl_p <= (st.session_state.aapl_last_price - aapl_trigger):
            cost = 5.0 * aapl_p
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                qty = 5.0
                st.session_state.aapl_holdings = qty
                st.session_state.aapl_buy_price = aapl_p
                record_trade("AAPL", "ПОКУПКА (АВТО)", qty, aapl_p, cost)
        elif st.session_state.aapl_holdings > 0 and aapl_p >= (st.session_state.aapl_buy_price + aapl_trigger):
            revenue = st.session_state.aapl_holdings * aapl_p
            st.session_state.balance += revenue
            record_trade("AAPL", "ПРОДАЖБА (АВТО)", st.session_state.aapl_holdings, aapl_p, revenue)
            st.session_state.aapl_holdings = 0.0
            st.session_state.aapl_buy_price = 0.0
            st.session_state.aapl_last_price = aapl_p

# --- РЪЧНО УПРАВЛЕНИЕ С ПОТРЕБИТЕЛСКИ СУМИ ($) ---
st.subheader("⚡ Ръчно управление с избор на сума ($)")
inv_col1, inv_col2, inv_col3 = st.columns(3)

with inv_col1:
    st.write("**BTC (Bitcoin)**")
    btc_amount_usd = st.number_input("Сума за BTC ($)", min_value=10.0, max_value=50000.0, value=500.0, step=50.0, key="btc_inv")
    if st.button("Купи BTC с тази сума") and btc_p:
        if st.session_state.balance >= btc_amount_usd:
            bought_qty = btc_amount_usd / btc_p
            old_val = st.session_state.btc_holdings * st.session_state.btc_buy_price
            new_qty = st.session_state.btc_holdings + bought_qty
            st.session_state.btc_buy_price = (old_val + btc_amount_usd) / new_qty if new_qty > 0 else btc_p
            st.session_state.btc_holdings = new_qty
            st.session_state.balance -= btc_amount_usd
            record_trade("BTC", "ПОКУПКА (РЪЧНА)", bought_qty, btc_p, btc_amount_usd)
            st.rerun()
        else:
            st.error("Нямаш достатъчно свободен баланс!")
    if st.button("Продай всички BTC") and btc_p and st.session_state.btc_holdings > 0:
        rev = st.session_state.btc_holdings * btc_p
        st.session_state.balance += rev
        record_trade("BTC", "ПРОДАЖБА (РЪЧНА)", st.session_state.btc_holdings, btc_p, rev)
        st.session_state.btc_holdings = 0.0
        st.session_state.btc_buy_price = 0.0
        st.rerun()

with inv_col2:
    st.write("**Gold (XAU/USD)**")
    gold_amount_usd = st.number_input("Сума за Gold ($)", min_value=10.0, max_value=50000.0, value=500.0, step=50.0, key="gold_inv")
    if st.button("Купи Gold с тази сума") and gold_p:
        if st.session_state.balance >= gold_amount_usd:
            bought_qty = gold_amount_usd / gold_p
            old_val = st.session_state.gold_holdings * st.session_state.gold_buy_price
            new_qty = st.session_state.gold_holdings + bought_qty
            st.session_state.gold_buy_price = (old_val + gold_amount_usd) / new_qty if new_qty > 0 else gold_p
            st.session_state.gold_holdings = new_qty
            st.session_state.balance -= gold_amount_usd
            record_trade("XAU/USD", "ПОКУПКА (РЪЧНА)", bought_qty, gold_p, gold_amount_usd)
            st.rerun()
        else:
            st.error("Нямаш достатъчно свободен баланс!")
    if st.button("Продай всичко Gold") and gold_p and st.session_state.gold_holdings > 0:
        rev = st.session_state.gold_holdings * gold_p
        st.session_state.balance += rev
        record_trade("XAU/USD", "ПРОДАЖБА (РЪЧНА)", st.session_state.gold_holdings, gold_p, rev)
        st.session_state.gold_holdings = 0.0
        st.session_state.gold_buy_price = 0.0
        st.rerun()

with inv_col3:
    st.write("**AAPL (Apple Акции)**")
    aapl_amount_usd = st.number_input("Сума за AAPL ($)", min_value=10.0, max_value=50000.0, value=500.0, step=50.0, key="aapl_inv")
    if st.button("Купи AAPL с тази сума") and aapl_p:
        if st.session_state.balance >= aapl_amount_usd:
            bought_qty = aapl_amount_usd / aapl_p
            old_val = st.session_state.aapl_holdings * st.session_state.aapl_buy_price
            new_qty = st.session_state.aapl_holdings + bought_qty
            st.session_state.aapl_buy_price = (old_val + aapl_amount_usd) / new_qty if new_qty > 0 else aapl_p
            st.session_state.aapl_holdings = new_qty
            st.session_state.balance -= aapl_amount_usd
            record_trade("AAPL", "ПОКУПКА (РЪЧНА)", bought_qty, aapl_p, aapl_amount_usd)
            st.rerun()
        else:
            st.error("Нямаш достатъчно свободен баланс!")
    if st.button("Продай всичко AAPL") and aapl_p and st.session_state.aapl_holdings > 0:
        rev = st.session_state.aapl_holdings * aapl_p
        st.session_state.balance += rev
        record_trade("AAPL", "ПРОДАЖБА (РЪЧНА)", st.session_state.aapl_holdings, aapl_p, rev)
        st.session_state.aapl_holdings = 0.0
        st.session_state.aapl_buy_price = 0.0
        st.rerun()

st.divider()

# --- РЕАЛНА ТЪРГОВСКА ГРАФИКА (TRADINGVIEW) ---
st.subheader("📊 Реална Пазарна Графика (TradingView)")

tradingview_code = """
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container" style="height:500px;width:100%">
  <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {
  "autosize": true,
  "symbol": "BINANCE:BTCUSDT",
  "interval": "1",
  "timezone": "Europe/Sofia",
  "theme": "dark",
  "style": "1",
  "locale": "bg",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "hide_side_toolbar": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_chart"
}
  );
  </script>
</div>
<!-- TradingView Widget END -->
"""

st.components.v1.html(tradingview_code, height=520)

st.divider()

# --- ДНЕВНИК НА СДЕЛКИТЕ ---
st.subheader("📋 Дневник на сделките")
if st.session_state.trades:
    for trade in reversed(st.session_state.trades):
        st.write(f"🕒 **{trade['Час']}** | {trade['Актив']} | **{trade['Тип']}** | Сума: **{trade['Сума USD']}** | Бр: {trade['Количество']} | Цена: {trade['Цена']} | Баланс: {trade['Баланс']}")
else:
    st.info("Все още няма извършени сделки.")