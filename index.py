import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальный Мониторинг", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- ФУНКЦИЯ-ОЧИСТИТЕЛЬ (решает проблему TypeError и 0 руб) ---
def clean_money(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Оставляем только ПЕРВОЕ число, которое находим в строке
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data():
    try:
        # Склад (80 столбцов)
        df_s = pd.read_csv(URL_SKLAD).iloc[:100, 0:80].fillna("")
        # Логистика 2026
        df_l = pd.read_csv(URL_LOGISTIC).fillna("")
        return df_s, df_l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l_raw = load_data()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS SYSTEM")
page = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if page == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 ПОЛНЫЙ РЕЕСТР СКЛАДА</h1>", unsafe_allow_html=True)
    if not df_s.empty:
        # Фильтры
        st.sidebar.subheader("🔍 Фильтрация")
        p_list = ["Все"] + sorted(df_s.iloc[:, 1].unique().astype(str).tolist())
        sel_p = st.sidebar.selectbox("Партнер:", p_list)
        
        df_f = df_s.copy()
        if sel_p != "Все":
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_p]

        # Метрики (Кассы - ст. 6, ФН - ст. 7 и 8)
        kkt = df_f.iloc[:, 5].apply(clean_money).sum()
        fn = df_f.iloc[:, 6].apply(clean_money).sum() + df_f.iloc[:, 7].apply(clean_money).sum()

        c1, c2 = st.columns(2)
        c1.metric("КАССЫ (ШТ)", f"{int(kkt)}")
        c2.metric("ФН (ШТ)", f"{int(fn)}")

        st.dataframe(df_f, use_container_width=True)

        # График-бублик
        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], 
                         hole=0.5, title="🔵 Доли касс по городам")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА И ПОСЫЛКИ 2026</h1>", unsafe_allow_html=True)
    if not df_l_raw.empty:
        # Берем столбцы B, K, L (весь массив)
        df_l = df_l_raw.copy()
        
        st.sidebar.subheader("🔍 Поиск")
        search = st.sidebar.text_input("Введи номер или город:")
        if search:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Сумма денег (Столбец L - индекс 11)
        df_l['Sum'] = df_l.iloc[:, 11].apply(clean_money)
        total_m = df_l['Sum'].sum()

        col1, col2 = st.columns(2)
        col1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_m:,.0f} ₽".replace(',', ' '))
        col2.metric("ВСЕГО ЗАПИСЕЙ", len(df_l))

        st.dataframe(df_l.iloc[:, 0:80], use_container_width=True)

        if total_m > 0:
            fig_l = px.pie(df_l[df_l['Sum']>0], values='Sum', names=df_l.columns[1], 
                           hole=0.5, title="📊 Обязательства по партнерам")
            st.plotly_chart(fig_l, use_container_width=True)
