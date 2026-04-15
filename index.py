import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone (широкий экран)
st.set_page_config(page_title="RBS: Глобальный Контроль", layout="wide")

# Дизайн и цвета тревоги
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    .alarm-red { background-color: #FFEBEE; padding: 15px; border-radius: 10px; border-left: 5px solid #FF5252; color: #B71C1C; margin-bottom: 10px; font-weight: bold; }
    .alarm-green { background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; color: #1B5E20; margin-bottom: 10px; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Чистка данных от текста (решает TypeError)
def get_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data(url):
    try:
        # Забираем всё до 80-го столбца
        return pd.read_csv(url).iloc[:100, 0:80].fillna("")
    except: return pd.DataFrame()

# --- САЙДБАР (МЕНЮ) ---
st.sidebar.title("💎 RBS COMMAND")
page = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if page == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 СКЛАД: ФИЛЬТРЫ И ТРЕВОГИ</h1>", unsafe_allow_html=True)
    df_s = load_data(URL_SKLAD)
    
    if not df_s.empty:
        # Фильтры склада
        st.sidebar.subheader("🔍 Настройка отображения")
        p_list = sorted(df_s.iloc[:, 1].unique().astype(str))
        c_list = sorted(df_s.iloc[:, 2].unique().astype(str))
        
        sel_p = st.sidebar.multiselect("Партнеры (Отправители):", p_list)
        sel_c = st.sidebar.multiselect("Города/Склады:", c_list)

        df_f = df_s.copy()
        if sel_p: df_f = df_f[df_f.iloc[:, 1].astype(str).isin(sel_p)]
        if sel_c: df_f = df_f[df_f.iloc[:, 2].astype(str).isin(sel_c)]

        # --- ТРЕВОГИ ---
        kkt = df_f.iloc[:, 5].apply(get_num).sum()
        fn = df_f.iloc[:, 6].apply(get_num).sum() + df_f.iloc[:, 7].apply(get_num).sum()

        st.subheader("🚨 Статус запасов:")
        if kkt < 3:
            st.markdown(f"<div class='alarm-red'>🔴 КРИТИЧЕСКИЙ ОСТАТОК КАСС: {int(kkt)} шт! Нужно пополнение.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alarm-green'>🟢 Касс в наличии: {int(kkt)} шт. (Запас в норме)</div>", unsafe_allow_html=True)
        
        if fn < 5:
            st.markdown(f"<div class='alarm-red'>🔴 МАЛО ФН: Всего {int(fn)} шт. Срочно проверь закупки!</div>", unsafe_allow_html=True)

        st.divider()
        st.write("### 📋 Полный массив склада (80 столбцов)")
        st.dataframe(df_f, use_container_width=True)

        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], hole=0.5, title="Распределение касс")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА: ВСЕ ПОЛУЧАТЕЛИ</h1>", unsafe_allow_html=True)
    df_l = load_data(URL_LOGISTIC)
    
    if not df_l.empty:
        # Глубокая фильтрация логистики
        st.sidebar.subheader("🔍 Фильтры логистики")
        search = st.sidebar.text_input("Поиск (номер/имя/город):")
        
        # Фильтр по Партнеру (B) и Получателю (C или D - зависит от твоей таблицы)
        partners_l = sorted(df_l.iloc[:, 1].unique().astype(str))
        sel_lp = st.sidebar.multiselect("Кто отправил (Партнер):", partners_l)
        
        # Поиск получателя по всему массиву через текстовое поле
        df_res = df_l.copy()
        if sel_lp: df_res = df_res[df_res.iloc[:, 1].astype(str).isin(sel_lp)]
        if search:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Итоги
        money = df_res.iloc[:, 11].apply(get_num).sum() # Столбец L
        c1, c2 = st.columns(2)
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{money:,.0f} ₽".replace(',', ' '))
        c2.metric("СТРОК В РАБОТЕ", len(df_res))

        st.write("### 📋 Полный массив логистики (Все данные)")
        st.dataframe(df_res, use_container_width=True, height=500)

        if money > 0:
            fig_l = px.pie(df_res, values=df_res.iloc[:, 11].apply(get_num), names=df_res.columns[1], 
                           hole=0.5, title="Деньги по отправителям")
            st.plotly_chart(fig_l, use_container_width=True)
            
