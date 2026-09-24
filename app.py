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

# --- ИНЖЕКТИРАНЕ НА МОДЕРЕН И КОМПАКТЕН CSS ---
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
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

# --- УПРАВЛЕНИЕ НА СЪСТОЯНИЕТО (SESSION STATE) ---
if "users_db" not in st.session_state:
    st.session_state.users_db = {"admin": "admin123"} # База с регистрирани потребители
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

# --- ЦЕНИ НА АКТИВИТЕ ---
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

# --- ФОРМА ЗА ВХОД И РЕГИСТРАЦИЯ ---
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
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Грешно потребителско име или парола!")
                        
        with tab_reg:
            with st.form("reg_form"):
                r_user = st.text_input("Ново потребителско име", key="r_u")
                r_pass = st.text_input("Нова парола", type="password", key="r_p")
                submit_r = st.form_submit_button("Регистрирай се и запази")
                
                if submit_r:
                    if r_user and r_pass:
                        if r_user in st.session_state.users_db:
                            st.warning("Това потребителско име вече съществува!")
                        else:
                            st.session_state.users_db[r_user] = r_pass
                            st.session_state.logged_in = True
                            st.session_state.username = r_user
                            st.success("Регистрацията е успешна! Влизане...")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.error("Моля, попълнете всички полета.")

else:
    # --- СТРАНИЧНА ЛЕНТА ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        st.markdown("---")
        menu = st.radio("Меню", [
            "📊 Криптовалути", 
            "🪙 Благородни Метали", 
            "📈 Акции", 
            "💰 Портфейл & Изтегляне", 
            "⚙️ Автоматични Ордери (TP/SL)"
        ])
        st.markdown("---")
        if st.button("Изход (Logout)"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # --- ФУНКЦИЯ ЗА ТЪРГОВИЯ (УНИВЕРСАЛНА) ---
    def render_trading_section(asset_list, title):
        st.title(title)
        
        # Общ баланс метрики
        crypto_val = sum(st.session_state.portfolio[k] * prices[k] for k in prices)
        total_nw = st.session_state.usd_balance + crypto_val
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Общ Баланс", f"${total_nw:,.2f}")
        m2.metric("Свободни Долари", f"${st.session_state.usd_balance:,.2f}")
        m3.metric("Активи Стойност", f"${crypto_val:,.2f}")
        st.markdown("---")
        
        c_left, c_right = st.columns([1.5, 1])
        
        with c_left:
            st.subheader("Пазарна Графика & Преглед")
            chart_df = pd.DataFrame(np.random.randn(15, len(asset_list)) * 5 + 100, columns=asset_list)
            st.line_chart(chart_df)
            
        with c_right:
            st.subheader("Поръчка (Купи / Продай)")
            sel_asset = st.selectbox("Изберете актив", asset_list)
            cur_p = prices[sel_asset]
            st.info(f"Текуща цена за 1 {sel_asset}: **${cur_p:,.2f}**")
            
            # Сума в долари
            amount_usd = st.number_input("Сума в долари ($)", min_value=1.0, max_value=max(float(st.session_state.usd_balance), 1.0), value=100.0, step=10.0)
            slider_usd = st.slider("Слайдър сума ($)", 0.0, max(float(st.session_state.usd_balance), 1.0), float(amount_usd))
            final_usd = slider_usd if slider_usd != 100.0 else amount_usd
            
            # Ордери тип
            order_type = st.selectbox("Тип ордер", ["Пазарен (Market)", "Лимитен (Limit Order)"])
            if order_type == "Лимитен (Limit Order)":
                st.number_input("Целева цена за изпълнение ($)", value=cur_p)
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🟢 КУПУВАЙ"):
                    if st.session_state.usd_balance >= final_usd:
                        st.session_state.u