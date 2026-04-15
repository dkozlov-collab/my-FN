import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone (широкий экран)
st.set_page_config(page_title="RBS GLOBAL 2026", layout="wide")

# Стильный дизайн
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; border-bottom: 2px solid #E0E0E0; }
    h1 { color: #1A237E !important; text-align: center; font-family: 'Arial', sans-serif; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
    .main-header { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border-left: 10px solid #007BFF; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- УМНЫЙ ОБРАБОТЧИК ДАННЫХ ---
def parse_money(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Вытаскиваем только ПЕРВОЕ число из строки (решает проблему текста в ячейках)
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(URL_SKLAD).iloc[:100, 0:80].fillna("")
        l = pd.read_csv(URL_LOGISTIC).fillna("")
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

# --- МЕНЮ ---
st.sidebar.markdown("### 💎 RBS CONTROL PANEL")
mode = st.sidebar.radio("ВЫБОР РАЗДЕЛА:", ["🏠 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

df_s, df_l_raw = load_all()

if mode == "🏠 СКЛАД И ОСТАТКИ":
    st.markdown("<div class='main-header'><h1>📦 СКЛАД И ТЕКУЩИЕ ОСТАТКИ</h1></div>", unsafe_allow_html=True)
    
    if not df_s.empty:
        # Фильтры
        st.sidebar.subheader("🔍 Фильтрация")
        p_list = ["Все"] + sorted(df_s.iloc[:, 1].unique().astype(str).tolist())
        sel_p = st.sidebar.selectbox("Выберите Партнера:", p_list)
        
        df_f = df_s.copy()
        if sel_p != "Все":
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_p]

        # Итоги (Кассы - 6 ст., ФН - 7 и 8 ст.)
        kkt = df_f.iloc[:, 5].apply(parse_money).sum()
        fn15 = df_f.iloc[:, 6].apply(parse_money).sum()
        fn36 = df_f.iloc[:, 7].apply(parse_money).sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("КАССЫ (ШТ)", f"{int(kkt)}")
        c2.metric("ФН-15 (ШТ)", f"{int(fn15)}")
        c3.metric("ФН-36 (ШТ)", f"{int(fn36)}")

        st.write("### 📋 Реестр остатков (Полный массив)")
        st.dataframe(df_f, use_container_width=True, height=450)

        # ГРАФИК СКЛАДА
        if kkt > 0:
            st.divider()
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], 
                         hole=0.5, title="🔵 Распределение касс по городам",
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Ошибка загрузки Склада")

else:
    st.markdown("<div class='main-header'><h1>🚚 ЛОГИСТИКА И ОБЯЗАТЕЛЬСТВА 2026</h1></div>", unsafe_allow_html=True)
    
    if not df_l_raw.empty:
        # Берем данные (B, K, L)
        df_l = df_l_raw.iloc[:, [1, 10, 11]].copy()
        df_l.columns = ['Партнер', 'Номера/Детали', 'Обязательства']
        
        # Фильтры
        st.sidebar.subheader("🔍 Поиск")
        search = st.sidebar.text_input("Введи номер или город:")
        
        if search:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Сумма обязательств
        df_l['Чистые Деньги'] = df_l['Обязательства'].apply(parse_money)
        total_m = df_l['Чистые Деньги'].sum()

        col1, col2 = st.columns(2)
        col1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_m:,.0f} ₽".replace(',', ' '))
        col2.metric("ВСЕГО ПОЗИЦИЙ", len(df_l))
        st.write("### 📦 Список отправлений")
        st.dataframe(df_l[['Партнер', 'Номера/Детали', 'Обязательства']], use_container_width=True, height=500)

        # ГРАФИК ЛОГИСТИКИ
        if total_m > 0:
            st.divider()
            fig_l = px.pie(df_l[df_l['Чистые Деньги'] > 0], values='Чистые Деньги', names='Партнер', 
                           hole=0.5, title="📊 Обязательства по партнерам",
                           color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig_l, use_container_width=True)
        
        csv = df_l.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 СКАЧАТЬ В EXCEL", csv, "RBS_Logistics.csv", "text/csv")

else:
    st.error("Ошибка загрузки Логистики")
