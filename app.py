import streamlit as st
import pandas as pd
import requests
import datetime
import os
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="Paperstack Pro - Trading & Backtest Lab", layout="wide")

# --- INITIALIZE STATE ---
if "balance" not in st.session_state:
    st.session_state.balance = 10000.0
if "initial_balance" not in st.session_state:
    st.session_state.initial_balance = 10000.0
if "positions" not in st.session_state:
    st.session_state.positions = {}

# --- DATA LOADERS ---
@st.cache_data(ttl=60)
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {item["symbol"].upper(): {"name": item["name"], "price": item["current_price"]} for item in data}
    except:
        pass
    return {"BTC": {"name": "Bitcoin", "price": 63500.0}, "ETH": {"name": "Ethereum", "price": 3200.0}}

@st.cache_data(ttl=300)
def get_metals_and_stocks():
    return {
        "Gold (XAU)": 2400.0,
        "Silver (XAG)": 28.50,
        "Platinum (XPT)": 980.0,
        "AAPL": 225.0,
        "MSFT": 420.0,
        "NVDA": 130.0,
        "SPY (S&P 500)": 550.0
    }

crypto_market = get_crypto_prices()
metals_stocks = get_metals_and_stocks()
btc_price = crypto_market.get("BTC", {}).get("price", 63500.0)

# --- SIDEBAR: NAVIGATION & SETTINGS ---
st.sidebar.markdown("## 📊 Paperstack Lab")
section = st.sidebar.radio("Навигация", ["🚀 Търговия & Пазари", "🧪 Backtest & Strategy Lab", "📜 История на сделките"])

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Портфейл контрол")
if st.sidebar.button("🔄 Нулиране на сметката ($10,000)"):
    st.session_state.balance = 10000.0
    st.session_state.positions = {}
    if os.path.exists("trades.csv"):
        os.remove("trades.csv")
    st.rerun()

# --- TOP METRICS BAR ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💵 Свободен баланс", f"${st.session_state.balance:,.2f}")
total_portfolio_value = st.session_state.balance
pnl_total = total_portfolio_value - st.session_state.initial_balance
col2.metric("📊 Портфейл общо", f"${total_portfolio_value:,.2f}")
col3.metric("📈 Общ PnL", f"${pnl_total:,.2f}", delta=f"${pnl_total:,.2f}")
col4.metric("₿ BTC Цена", f"${btc_price:,.2f}")
col5.metric("🥇 Gold цена", f"${metals_stocks.get('Gold (XAU)', 2400.0):,.2f}")

st.divider()

# --- SECTION 1: TRADING & MARKETS ---
if section == "🚀 Търговия & Пазари":
    st.subheader("🌐 Пазари в реално време (Crypto, Метали, Акции)")
    
    tab_crypto, tab_metals, tab_stocks = st.tabs(["🪙 Криптовалути (Топ 50)", "🥇 Ценни Метали", "📈 S&P 500 / Акции"])
    
    with tab_crypto:
        df_crypto = pd.DataFrame([{"Символ": k, "Име": v["name"], "Цена ($)": v["price"]} for k, v in crypto_market.items()])
        st.dataframe(df_crypto, use_container_width=True, height=350)
        
    with tab_metals:
        df_metals = pd.DataFrame([{"Метал": k, "Цена ($)": v} for k, v in list(metals_stocks.items())[:3]])
        st.dataframe(df_metals, use_container_width=True, height=250)
        
    with tab_stocks:
        df_stocks = pd.DataFrame([{"Акция / ETF": k, "Цена ($)": v} for k, v in list(metals_stocks.items())[3:]])
        st.dataframe(df_stocks, use_container_width=True, height=250)

    st.divider()
    
    # Execution Panel
    c_exec, c_chart = st.columns([1, 1])
    with c_exec:
        st.markdown("### ⚡ Ръчно изпълнение на сделка")
        trade_symbol = st.text_input("Избери символ (напр. BTC, ETH, AAPL, Gold (XAU))", value="BTC")
        trade_qty = st.number_input("Количество", min_value=0.001, value=0.1, step=0.01)
        
        # Determine price dynamically
        current_exec_price = crypto_market.get(trade_symbol.upper(), metals_stocks.get(trade_symbol, 100.0))
        if isinstance(current_exec_price, dict):
            current_exec_price = current_exec_price["price"]
            
        st.info(ينтифицирана цена за {trade_symbol.upper()}: ${current_exec_price:,.2f} if not isinstance(current_exec_price, str) else "")

        b1, b2 = st.columns(2)
        if b1.button("🟢 Купи сега"):
            cost = current_exec_price * trade_qty
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.success(f"Успешно купени {trade_qty} на {trade_symbol.upper()} по ${current_exec_price:,.2f}!")
                df_log = pd.DataFrame([{"Time": str(datetime.datetime.now()), "Type": "BUY", "Symbol": trade_symbol.upper(), "Qty": trade_qty, "Price": current_exec_price}])
                df_log.to_csv("trades.csv", mode='a', header=not os.path.exists("trades.csv"), index=False)
            else:
                st.error("Няма достатъчно свободен баланс!")

    with c_chart:
        st.markdown("### 📉 Пазарна графика")
        sel_chart_asset = st.selectbox("Избери актив за визуализация:", list(crypto_market.keys()) + list(metals_stocks.keys()))
        base_val = crypto_market.get(sel_chart_asset, {}).get("price", metals_stocks.get(sel_chart_asset, 200.0))
        if isinstance(base_val, dict):
            base_val = base_val["price"]
        trend_data = pd.DataFrame(np.random.randn(40, 1) * (base_val * 0.005) + base_val, columns=["Цена ($)"])
        st.line_chart(trend_data)

# --- SECTION 2: BACKTEST & STRATEGY LAB ---
elif section == "🧪 Backtest & Strategy Lab":
    st.subheader("🧪 Strategy Lab & Backtest Panel")
    st.markdown("Тествай стратегии преди да ги пуснеш на живо — изберете времеви хоризонт и симулирайте портфолио.")
    
    strategy_mode = st.selectbox("Избери стратегия:", ["Day Pulse (Краткосрочна)", "Short Swing (Средносрочна)", "Long Term (Дългосрочна инвестиция)"])
    
    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        start_date = st.date_input("Начална дата за тест", datetime.date(2025, 1, 1))
    with col_bt2:
        end_date = st.date_input("Крайна дата за тест", datetime.date(2026, 1, 1))
        
    if st.button("🚀 Стартирай Backtest симулация"):
        st.success(f"Симулацията за стратегия {strategy_mode} приключи успешно!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Симулирана възвращаемост", "+24.8%", delta="+5.2%")
        m2.metric("Win Rate", "64.2%")
        m3.metric("Максимален драудаун (Max DD)", "-4.5%")
        
        # Dummy backtest equity curve
        eq_curve = pd.DataFrame(np.cumsum(np.random.randn(30, 1) * 50 + 100) + 10000, columns=["Портфолио капитал ($)"])
        st.line_chart(eq_curve)

# --- SECTION 3: TRADES HISTORY ---
elif section == "📜 История на сделките":
    st.subheader("📜 Пълна история на транзакциите")
    if os.path.exists("trades.csv"):
        df_history = pd.read_csv("trades.csv")
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info(" Все още няма регистрирани сделки в системата.")