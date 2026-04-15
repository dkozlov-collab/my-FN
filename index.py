import streamlit as st
import pandas as pd

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальное управление", layout="wide")

# --- ССЫЛКИ НА ТАБЛИЦЫ ---
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- ОБЩИЕ ИНСТРУМЕНТЫ (ЧИСТКА ДАННЫХ) ---
def to_num(x):
    try: return float(str(x).replace(' ', '').replace('₽', '').replace(',', '.'))
    except: return 0

# --- ПАПКА 1: ЛОГИКА СКЛАДА ---
def run_sklad():
    st.markdown("<h2 style='color: #007BFF;'>📦 СКЛАД И ОСТАТКИ ФН</h2>", unsafe_allow_html=True)
    try:
        df = pd.read_csv(URL_SKLAD).iloc[:80, 0:17].fillna(0)
        st.write("### Текущий массив склада (A:Q)")
        st.dataframe(df, use_container_width=True)
    except:
        st.error("Ошибка доступа к таблице Склада!")

# --- ПАПКА 2: ЛОГИКА ЛОГИСТИКИ 2026 ---
def run_logistics():
    st.markdown("<h2 style='color: #FF9800;'>🚚 ЛОГИСТИКА И ПОСЫЛКИ 2026</h2>", unsafe_allow_html=True)
    try:
        df_raw = pd.read_csv(URL_LOGISTIC).fillna("")
        # Берем твои столбцы: B(1), K(10), L(11)
        df = df_raw.iloc[:, [1, 10, 11]]
        df.columns = ['Партнер / Город', 'Номера посылок', 'Обязательства (₽)']
        
        # Поиск
        search = st.text_input("🔍 Найти посылку или город:")
        if search:
            df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        # Считаем деньги
        total = df['Обязательства (₽)'].apply(to_num).sum()
        st.metric("СУММА ПО ВЫБОРКЕ", f"{total:,.0f} ₽".replace(',', ' '))
        
        st.dataframe(df, use_container_width=True, height=500)
        
        # Кнопка скачивания
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Скачать этот отчет в Excel", data=csv, file_name='RBS_Logistics_2026.csv')
    except:
        st.error("Ошибка доступа к таблице Логистики!")

# --- ГЛАВНЫЙ ЗАПУСК (МЕНЮ) ---
st.sidebar.title("💎 RBS SYSTEM")
choice = st.sidebar.radio("КУДА ЗАЙДЕМ?", ["Склад", "Логистика 2026"])

if choice == "Склад":
    run_sklad()
else:
    run_logistics()
