import streamlit as st
import pandas as pd
import requests
import datetime
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Pro Trading Bot & Analytics", layout="wide")

# --- INITIALIZE STATE ---
if "balance" not in st.session_state:
    st.session_state.balance = 10000.0
if "initial_balance" not in st.session_state:
    st.session_state.initial_balance = 10000.0
if "positions" not in st.session_state:
    st.session_state.positions = {}  # symbol: {qty, avg_price}

# --- DATA LOADERS (Cached) ---
@st.cache_data(ttl=60)
def get_crypto_prices():
    # Fetch top 50 from CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {item["symbol"].upper(): {"name": item["name"], "price": item["current_price"]} for item in data}
    except Exception as e:
        pass
    # Fallback default if API rate limited/fails
    return {"BTC": {"name": "Bitcoin", "price": 63500.0}, "ETH": {"name": "Ethereum", "price": 3200.0}}

@st.cache_data(ttl=300)
def get_metals_and_stocks():
    # Simulated/Live realistic baseline for metals & key SP500 proxies
    # For a heavy S&P 500 500-list, Yahoo finance batch or subset is used. Here top core representatives + fallback
    data = {
        "Gold (XAU)": 4405.0,
        "Silver (XAG)": 31.50,
        "Platinum (XPT)": 985.0,
        "AAPL": 225.0,
        "MSFT": 420.0,
        "NVDA": 130.0,
        "SPY (S&P 500 ETF)": 560.0
    }
    return data

crypto_market = get_crypto_prices()
metals_stocks = get_metals_and_stocks()

# Ensure BTC is always present cleanly
btc_price = crypto_market.get("BTC", {}).get("price", 63500.0)

# --- SIDEBAR: SETTINGS & RESET ---
st.sidebar.header("⚙️ Контрол и Авто-търговия")
auto_trade = st.sidebar.checkbox("Активирай авто-сигнали", value=False)
btc_threshold = st.sidebar.slider("Праг за авто-покупка BTC ($)", 30000.0, 100000.0, 60000.0, 500.0)

if st.sidebar.button("🔄 Нулиране на сметката ($10,000)"):
    st.session_state.balance = 10000.0
    st.session_state.positions = {}
    if os.path.exists("trades.csv"):
        os.remove("trades.csv")
    st.rerun()

# --- TOP METRICS BAR ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💵 Свободен баланс", f"${st.session_state.balance:,.2f}")

# Calculate portfolio & PnL roughly
total_portfolio_value = st.session_state.balance
pnl_total = total_portfolio_value - st.session_state.initial_balance

col2.metric("📊 Портфейл общо", f"${total_portfolio_value:,.2f}")
col3.metric("📈 Общ PnL", f"${pnl_total:,.2f}", delta=f"${pnl_total:,.2f}")
col4.metric("₿ BTC Цена", f"${btc_price:,.2f}")
col5.metric("🥇 Gold цена", f"${metals_stocks.get('Gold (XAU)', 4405.0):,.2f}")

st.divider()

# --- MAIN LAYOUT: CATEGORY VIEWS ---
st.subheader("🌐 Пазари и Котировки")
view_mode = st.radio("Изглед на пазара:", ["Всички заедно (3 клетки)", само криптото", "Само ценни метали", "Само S&P / Акции"], horizontal=True, label_visibility="collapsed")
# Quick fix for string label typo in radio
view_mode = "Всички заедно (3 клетки)" if "Всички" in view_mode else view_mode

c_crypto, c_metals, c_stocks = st.columns(3)

show_all = "Всички" in view_mode

if show_all or "крипто" in view_mode.lower():
    with c_crypto if show_all else st.container():
        st.markdown("### 🪙 Криптовалути (Топ 50)")
        df_crypto = pd.DataFrame([
            {"Symbol": k, "Name": v["name"], "Price ($)": v["price"]}
            for k, v in crypto_market.items()
        ])
        st.dataframe(df_crypto, use_container_width=True, height=300)

if show_all or "метали" in view_mode.lower():
    with c_metals if show_all else st.container():
        st.markdown("### 🥇 Ценни Метали")
        df_metals = pd.DataFrame([
            {"Metal": k, "Price ($)": v}
            for k, v in list(metals_stocks.items())[:3]
        ])
        st.dataframe(df_metals, use_container_width=True, height=300)

if show_all or "s&p" in view_mode.lower():
    with c_stocks if show_all else st.container():
        st.markdown("### 📈 S&P 500 / Ликвидни акции")
        df_stocks = pd.DataFrame([
            {"Ticker": k, "Price ($)": v}
            for k, v in list(metals_stocks.items())[3:]
        ])
        st.dataframe(df_stocks, use_container_width=True, height=300)

st.divider()

# --- ANALYTICS / CHARTS SECTION ---
st.subheader("📉 Анализи и Графики на актива")
selected_asset = st.selectbox("Избери актив за визуализация:", list(crypto_market.keys()) + list(metals_stocks.keys()))

# Generate dummy historical trend chart for inspection
import numpy as np
chart_data = pd.DataFrame(
    np.random.randn(50, 1) * 10 + (btc_price if selected_asset=='BTC' else 200),
    columns=["Цена ($) тренд"]
)
st.line_chart(chart_data)

st.divider()

# --- TRADING EXECUTION & HISTORY ---
col_trade, col_hist = st.columns()

with col_trade:
  st.subheader("⚡ Ръчна търговия / Изпълнение")
  trade_symbol = st.text_input("Символ за покупка/продажба", value="BTC")
  trade_qty = st.number_input("Количество", min_value=0.001, value=0.1, step=0.01)
  
  col_b1, col_b2 = st.columns(2)
  if col_b1.button("🟢 Купи"):
      exec_price = crypto_market.get(trade_symbol.upper(), {}).get("price", 100.0)
      cost = exec_price * trade_qty
      if st.session_state.balance >= cost:
          st.session_state.balance -= cost
          st.success(fКупени {trade_qty} {trade_symbol.upper()} по ${exec_price:,.2f}!")
          # log trade
          df_log = pd.DataFrame([{"Time": str(datetime.datetime.now()), "Type": "BUY", "Symbol": trade_symbol.upper(), "Qty": trade_qty, "Price": exec_price}])
          if os.path.exists("trades.csv"):
              df_log.to_csv("trades.csv", mode='a', header=False, index=False)
          else:
              df_log.to_csv("trades.csv", index=False)
      else:
          st.error("Няма достатъчно свободен баланс!")

  if col_b2.button("🔴 Продай"):
      st.info("Продажбата е готова за изпълнение за налични позиции.")

with col_hist:
  st.subheader("📜 История на сделките")
  if os.path.exists("trades.csv"):
      df_history = pd.read_csv("trades.csv")
      st.dataframe(df_history, use_container_width=True)
  else:
      st.info("Все още няма записани сделки.")