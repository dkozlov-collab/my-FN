import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка
st.set_page_config(page_title="RBS: Регистрация", layout="wide", page_icon="📝")

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(val):
    try:
        # Убираем пробелы, валюту и превращаем в число
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except:
        return 0

@st.cache_data(ttl=15)
def load_data():
    try:
        # Читаем только первые 80 строк
        df = pd.read_csv(URL).head(80).fillna(0)
        # Убираем полностью пустые строки, если они есть
        df = df[df['Склад'] != 0]
        
        # Чистим цифры
        for col in ['Остатки ККТ', 'Итого сумма']:
            if col in df.columns:
                df[col] = df[col].apply(clean_num)
        return df
    except:
        return pd.DataFrame()

# ЗАГОЛОВОК
st.markdown("<h1 style='text-align: center;'>📝 ПОРТАЛ РЕГИСТРАЦИИ RBS</h1>", unsafe_allow_html=True)

df = load_data()

if not df.empty:
    # --- ФИЛЬТР ---
    partners = ["ВСЕ"] + sorted(df['Сервис Партнер'].unique().tolist())
    sel_p = st.sidebar.selectbox("Выбор Партнера", partners)
    
    if sel_p != "ВСЕ":
        df = df[df['Сервис Партнер'] == sel_p]

    # --- KPI ---
    c1, c2 = st.columns(2)
    kkt_sum = df['Остатки ККТ'].sum()
    c1.metric("Всего ККТ", f"{kkt_sum} шт")
    
    money_sum = df['Итого сумма'].sum() if 'Итого сумма' in df.columns else 0
    c2.metric("Сумма на складах", f"{money_sum:,.0f} ₽".replace(',', ' '))

    st.divider()

    # --- ГРАФИКИ (БЕЗОПАСНЫЕ) ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### 🍩 Доли складов")
        # Проверка: если ККТ = 0, круговой график не рисуем, чтобы не было ошибки
        if kkt_sum > 0:
            fig_pie = px.pie(df, values='Остатки ККТ', names='Склад', hole=0.5)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Нет данных для графика")

    with col_r:
        st.write("### 📊 Наличие")
        if kkt_sum > 0:
            st.bar_chart(df.set_index('Склад')['Остатки ККТ'])

    # ТАБЛИЦА
    st.write("### Реестр (1-80)")
    st.dataframe(df, use_container_width=True)

else:
    st.error("Не удалось прочитать таблицу. Проверь права доступа или ссылку.")
