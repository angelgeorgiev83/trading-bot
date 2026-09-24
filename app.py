import streamlit as st
import pandas as pd
import numpy as np
import time

# --- НАСТРОЙКА НА СТРАНИЦАТА ---
st.set_page_config(
    page_title="Professional Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ИНЖЕКТИРАНЕ НА СТИЛОВЕ ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d1117;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #f0f6fc !important;
        font-size: 15px !important;
    }
    .source-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- УПРАВЛЕНИЕ НА СЪСТОЯНИЕТО ---
if "users_db" not in st.session_state:
    st.session_state.users_db = {"angel": "123456"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "usd_balance" not in st.session_state:
    st.session_state.usd_balance = 12450.00
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "BTC": 0.0, "ETH": 0.0, "SOL": 0.0,
        "Злато (XAU)": 0.0, "Сребро (XAG)": 0.0,
        "Tesla (TSLA)": 0.0, "Apple (AAPL)": 0.0, "Microsoft (MSFT)": 0.0
    }

# --- ЦЕНИ И ИСТОЧНИЦИ ДАННИХ ---
prices = {
    "BTC": 64250.00,
    "ETH": 3120.00,
    "SOL": 145.20,
    "Злато (XAU)": 2350.00,
    "Сребро (XAG)": 28.50,
    "Tesla (TSLA)": 210.00,
    "Apple (AAPL)": 225.00,
    "Microsoft (MSFT)": 415.00
}

# --- ЕКРАН ЗА ВХОД И РЕГИСТРАЦИЯ ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔐 Платформа за Търговия")
        
        tab_login, tab_reg = st.tabs(["Вход", "Регистрация"])
        
        with tab_login:
            with st.form("login_form"):
                l_user = st.text_input("Потребителско име", key="l_u")
                l_pass = st.text_input("Парола", type="password", key="l_p")
                submit_l = st.form_submit_button("Вход в системата")
                
                if submit_l:
                    if l_user in st.session_state.users_db and st.session_state.users_db[l_user] == l_pass:
                        st.session_state.logged_in = True
                        st.session_state.username = l_user
                        st.success("Успешен вход!")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error("Грешно потребителско име или парола!")
                        
        with tab_reg:
            with st.form("reg_form"):
                r_user = st.text_input("Ново потребителско име", key="r_u")
                r_pass = st.text_input("Парола", type="password", key="r_p")
                submit_r = st.form_submit_button("Регистрирай се")
                
                if submit_r:
                    if r_user and r_pass:
                        st.session_state.users_db[r_user] = r_pass
                        st.session_state.logged_in = True
                        st.session_state.username = r_user
                        st.success("Регистрацията е успешна!")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error("Попълнете полетата.")

else:
    # --- СТРАНИЧНА ЛЕНТА С НАВИГАЦИЯ ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        st.markdown("---")
        
        menu = st.radio("Меню", [
            "📊 Криптовалути", 
            "🪙 Благородни Метали", 
            "📈 Акции", 
            "💰 Портфейл & Изтегляне", 
            "⚙️ Автоматични Ордери (TP/SL)"
        ], key="main_menu_radio")
        
        st.markdown("---")
        if st.button("Изход (Logout)"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # --- 1. КРИПТОВАЛУТИ ---
    if menu == "📊 Криптовалути":
        st.title("📊 Криптовалути - Пазар и Търговия")
        st.markdown('<div class="source-box">📡 <b>Източници на ценови данни:</b> Binance API, CoinGecko Feed & Kraken WebSocket</div>', unsafe_allow_html=True)
        
        active_list = ["BTC", "ETH", "SOL"]
        crypto_val = sum(st.session_state.portfolio[k] * prices[k] for k in prices)
        total_nw = st.session_state.usd_balance + crypto_val
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Общ Баланс", f"${total_nw:,.2f}")
        m2.metric("Свободни Долари", f"${st.session_state.usd_balance:,.2f}")
        m3.metric("Активи Стойност", f"${crypto_val:,.2f}")
        st.markdown("---")
        
        c_left, c_right = st.columns([1.5, 1])
        with c_left:
            st.subheader("Ценова Графика (Крипто)")
            chart_df = pd.DataFrame(np.random.randn(15, len(active_list)) * 120 + 30000, columns=active_list)
            st.line_chart(chart_df)
            
        with c_right:
            st.subheader("Поръчка (Купи / Продай)")
            sel_asset = st.selectbox("Изберете актив", active_list, key="sel_crypto")
            cur_p = prices[sel_asset]
            st.info("Цена за 1 актив: **$" + f"{cur_p:,.2f}" + "**")
            
            amount_usd = st.number_input("Сума в долари ($)", min_value=1.0, max_value=max(float(st.session_state.usd_balance), 1.0), value=100.0, step=10.0, key="amt_c")
            order_type = st.selectbox("Тип ордер", ["Пазарен (Market)", "Лимитен (Limit Order)"], key="ord_c")
            if order_type == "Лимитен (Limit Order)":
                st.number_input("Целева цена ($)", value=cur_p, key="lim_c")
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🟢 КУПУВАЙ", key="b_c"):
                    if st.session_state.usd_balance >= amount_usd:
                        st.session_state.usd_balance -= amount_usd
                        qty = amount_usd / cur_p
                        st.session_state.portfolio[sel_asset] += qty
                        st.success("Успеш