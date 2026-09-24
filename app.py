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

# --- ИНЖЕКТИРАНЕ НА МОДЕРЕН CSS (Тъмна тема и професионален дизайн) ---
st.markdown("""
    <style>
    /* Цялостен фон и шрифт /
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    / Стил за контейнери / карти /
    .css-1r6slb0, .stCard, div[data-testid="stVerticalBlock"] > div[style="background-color"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Персонализирани бутони /
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
    
    / Полета за въвеждане /
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d1117;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    
    / Страничен панел (Sidebar) /
    [data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #30363d;
    }
    
    / Заглавия */
    h1, h2, h3 {
        color: #f0f6fc;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- УПРАВЛЕНИЕ НА СЪСТОЯНИЕТО ЗА ВХОД (SESSION STATE) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- ФОРМА ЗА ВХОД / РЕГИСТРАЦИЯ (АКО НЕ Е ВЛЯЗЪЛ) ---
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
                    st.success("Успешен вход! Зареждане на панела...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Моля, попълнете всички полета.")
                    
        st.markdown("---")
        st.info("💡 Тестов достъп: Можете да въведете произволни данни за вход, за да разгледате демо интерфейса.")

else:
    # --- ОСНОВЕН ПАНЕЛ НА ПЛАТФОРМАТА (СЛЕД УСПЕШЕН ВХОД) ---
    
    # Странична лента за навигация
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/user-male-circle.png", width=80)
        st.write(f"Здравейте, {st.session_state.username}!")
        st.markdown("---")
        
        menu = st.radio("Навигация", ["📊 Търговия & Пазар", "💰 Портфейл", "⚙️ Настройки"])
        
        st.markdown("---")
        if st.button("Изход (Logout)"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # Основно съдържание според менюто
    if menu == "📊 Търговия & Пазар":
        st.title("📈 Пазарен Преглед & Търговия")
        
        # Горни метрики (Баланс, Печалба)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="Общ Баланс", value="$12,450.00", delta="+$340.50 (2.8%)")
        m2.metric(label="Свободни Средства", value="$4,120.50")
        m3.metric(label="Активни Позиции", value="3 броя")
        m4.metric(label="Дневен П&Л", value="+$180.20", delta="1.45%")
        
        st.markdown("---")
        
        # Секция за изпълнение на поръчка
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Ценова графика (Демо)")
            # Генериране на примерен график
            chart_data = pd.DataFrame(
                np.random.randn(20, 3) * 10 + 100,
                columns=['BTC/USD', 'ETH/USD', 'SOL/USD']
            )
            st.line_chart(chart_data)
            
        with col_right:
            st.subheader("Бърза Поръчка")
            trade_symbol = st.selectbox("Изберете актив", ["BTC/USD", "ETH/USD", "SOL/USD", "EUR/USD"])
            trade_type = st.radio("Тип сделка", ["Купува (BUY)", "Продава (SELL)"], horizontal=True)
            amount = st.number_input("Количество", min_value=0.01, value=1.00, step=0.01)
            
            # Примерна логика за цена (тук използваме твоя корегиран ред)
            current_exec_price = 64250.00 if "BTC" in trade_symbol else 3120.00
            st.info(f"Идентифицирана цена за {trade_symbol.upper()}: ${current_exec_price:,.2f}")
            
            if st.button("Изпълни поръчката"):
                st.success(f"Успешно изпълнена поръчка за {amount} {trade_symbol}!")

    elif menu == "💰 Портфейл":
        st.title("💰 Вашият Портфейл")
        st.write("Тук можете да следите вашите активи, депозити и тегления.")
        
        # Таблица с активи
        portfolio_df = pd.DataFrame({
            "Актив": ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)", "USDT"],
            "Количество": [0.45, 1.8, 14.5, 2100.00],
            "Текуща цена ($)": [64250.00, 3120.00, 145.20, 1.00],
            "Обща стойност ($)": [28912.50, 5616.00, 2105.40, 2100.00]
        })
        st.dataframe(portfolio_df, use_container_width=True)

    elif menu == "⚙️ Настройки":
        st.title("⚙️ Настройки на профила")
        st.text_input("Име за контакт", value=st.session_state.username)
        st.text_input("Имейл адрес", value="user@example.com")
        st.checkbox("Известия по имейл", value=True)
        st.checkbox("Двуфакторна автентикация (2FA)", value=False)
        
        if st.button("Запази промените"):
            st.success("Настройките бяха запазени успешно!")