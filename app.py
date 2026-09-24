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

# --- ИНЖЕКТИРАНЕ НА МОДЕРЕН CSS (С оправени текстове в менюто) ---
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
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 0 10px rgba(46, 160, 67, 0.5);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d1117;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #30363d;
    }
    /* Оправяне на видимостта на текстовете в радио бутоните в менюто */
    [data-testid="stSidebar"] .stRadio label {
        color: #f0f6fc !important;
        font-size: 16px !important;
    }
    h1, h2, h3 {
        color: #f0f6fc;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- УПРАВЛЕНИЕ НА СЪСТОЯНИЕТО ( SESSION STATE ) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "usd_balance" not in st.session_state:
    st.session_state.usd_balance = 12450.00
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "BTC": 0.0,
        "ETH": 0.0,
        "SOL": 0.0
    }

# --- ЦЕНИ НА АКТИВИТЕ ---
btc_price = 64250.00
eth_price = 3120.00
sol_price = 145.20

# --- ФОРМА ЗА ВХОД ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🔐 Вход в платформата")
        st.write("Моля, влезте в профила си, за да достъпите търговския панел.")
        
        with st.form("login_form"):
            username_input = st.text_input("Потребителско име или Имейл")
            password_input = st.text_input("Парола", type="password")
            submit_login = st.form_submit_button("Вход")
            
            if submit_login:
                if username_input and password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.success("Успешен вход! Зареждане...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Моля, попълнете всички полета.")
        st.markdown("---")
        st.info("💡 **Тестов достъп:** Въведете произволни данни, за да влезете.")

else:
    # --- СТРАНИЧНА ЛЕНТА ---
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/user-male-circle.png", width=80)
        st.write(f"Здравейте, **{st.session_state.username}**!")
        st.markdown("---")
        
        menu = st.radio("Навигация", ["📊 Търговия & Пазар", "💰 Портфейл", "🔄 Конвертиране", "⚙️ Настройки"])
        
        st.markdown("---")
        if st.button("Изход (Logout)"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # --- 1. ТЪРГОВИЯ & ПАЗАР ---
    if menu == "📊 Търговия & Пазар":
        st.title("📈 Пазарен Преглед & Търговия")
        
        crypto_value = (
            st.session_state.portfolio["BTC"] * btc_price +
            st.session_state.portfolio["ETH"] * eth_price +
            st.session_state.portfolio["SOL"] * sol_price
        )
        total_net_worth = st.session_state.usd_balance + crypto_value
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="Общ Баланс", value=f"${total_net_worth:,.2f}")
        m2.metric(label="Свободни Долари", value=f"${st.session_state.usd_balance:,.2f}")
        m3.metric(label="Стойност Крипто", value=f"${crypto_value:,.2f}")
        m4.metric(label="Пазарен статус", value="🟢 Активен")
        
        st.markdown("---")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Ценова графика (Демо)")
            chart_data = pd.DataFrame(
                np.random.randn(20, 3) * 10 + 100,
                columns=['BTC/USD', 'ETH/USD', 'SOL/USD']
            )
            st.line_chart(chart_data)
            
        with col_right:
            st.subheader("Бърза Поръчка")
            
            trade_symbol = st.selectbox("Изберете актив", ["BTC", "ETH", "SOL"])
            if trade_symbol == "BTC":
                current_price = btc_price
            elif trade_symbol == "ETH":
                current_price = eth_price
            else:
                current_price = sol_price
                
            st.info(f"Цена за 1 {trade_symbol}: ${current_price:,.2f}")
            
            amount_usd = st.number_input("Сума в долари ($)", min_value=1.0, max_value=float(st.session_state.usd_balance) if st.session_state.usd_balance > 0 else 1.0, value=100.0, step=10.0)
            
            max_slider = max(st.session_state.usd_balance, 1.0)
            slider_usd = st.slider("Изберете сума чрез слайдър ($)", min_value=0.0, max_value=float(max_slider), value=min(amount_usd, max_slider))
            
            final_usd = slider_usd if slider_usd != 100.0 else amount_usd
            
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                if st.button("🟢 Купувай (BUY)"):
                    if st.session_state.usd_balance >= final_usd and final_usd > 0:
                        st.session_state.usd_balance -= final_usd
                        purchased_amount = final_usd / current_price
                        st.session_state.portfolio[trade_symbol] += purchased_amount
                        st.success(f"Успешно купихте {purchased_amount:.4f} {trade_symbol} за ${final_usd:,.2f}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Нямате достатъчно свободни средства в долари!")
                        
            with col_b2:
                if st.button("🔴 Продавай (SELL)"):
                    required_crypto = final_usd / current_price
                    if st.session_state.portfolio[trade_symbol] >= required_crypto and required_crypto > 0:
                        st.session_state.portfolio[trade_symbol] -= required_crypto
                        st.session_state.usd_balance += final_usd