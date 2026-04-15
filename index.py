import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

# Дизайн
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 30px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ (Убедись, что они ведут на экспорт CSV)
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- ФУНКЦИЯ-ПЫЛЕСОС (Очищает данные от текста, оставляя только числа) ---
def clean_to_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Оставляем только цифры, точки и минусы
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data(url, cols=None):
    try:
        df = pd.read_csv(url).fillna(0)
        if cols: df = df.iloc[:100, cols] # Берем с запасом 100 строк
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return pd.DataFrame()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS SYSTEM 2026")
mode = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if mode == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 СКЛАД И ТЕКУЩИЕ ОСТАТКИ</h1>", unsafe_allow_html=True)
    df_s = load_data(URL_SKLAD, range(0, 17))
    
    if not df_s.empty:
        # Автопоиск колонок по смыслу
        p_col = df_s.columns[1] # Партнер
        c_col = df_s.columns[2] # Город
        
        # Фильтры в сайдбаре
        st.sidebar.subheader("🔍 Фильтры Склада")
        sel_p = st.sidebar.multiselect("Партнер:", sorted(df_s[p_col].unique().astype(str)))
        sel_c = st.sidebar.multiselect("Город:", sorted(df_s[c_col].unique().astype(str)))

        df_f = df_s.copy()
        if sel_p: df_f = df_f[df_f[p_col].astype(str).isin(sel_p)]
        if sel_c: df_f = df_f[df_f[c_col].astype(str).isin(sel_c)]

        # Метрики с ОЧИСТКОЙ (решает TypeError)
        kkt_count = df_f.iloc[:, 5].apply(clean_to_num).sum()
        fn_count = df_f.iloc[:, 6].apply(clean_to_num).sum() + df_f.iloc[:, 7].apply(clean_to_num).sum()
        
        m1, m2 = st.columns(2)
        m1.metric("ККТ В НАЛИЧИИ", f"{int(kkt_count)} шт")
        m2.metric("ФН (ОСТАТОК)", f"{int(fn_count)} шт")

        st.dataframe(df_f, use_container_width=True, hide_index=True)

        if kkt_count > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=c_col, hole=0.5, title="🔵 Доли ККТ по складам")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА И ПОСЫЛКИ 2026</h1>", unsafe_allow_html=True)
    # Берем столбцы B(1), K(10), L(11)
    df_l = load_data(URL_LOGISTIC, [1, 10, 11])
    
    if not df_l.empty:
        df_l.columns = ['Партнер/Город', 'Номера посылок', 'Обязательства']
        
        st.sidebar.subheader("🔍 Фильтры Логистики")
        search_track = st.sidebar.text_input("Поиск по номеру:")
        sel_lp = st.sidebar.multiselect("Партнер:", sorted(df_l['Партнер/Город'].unique().astype(str)))

        df_res = df_l.copy()
        if sel_lp: df_res = df_res[df_res['Партнер/Город'].astype(str).isin(sel_lp)]
        if search_track:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search_track, case=False).any(), axis=1)]

        # Считаем деньги (умный парсинг вытащит 0 руб)
        df_res['Money'] = df_res['Обязательства'].apply(clean_to_num)
        total_money = df_res['Money'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_money:,.0f} ₽".replace(',', ' '))
        c2.metric("ВСЕГО ПОСЫЛОК", len(df_res[df_res['Номера посылок'] != 0]))

        st.dataframe(df_res[['Партнер/Город', 'Номера посылок', 'Обязательства']], use_container_width=True, hide_index=True, height=500)

        if total_money > 0:
            fig_l = px.pie(df_res[df_res['Money'] > 0], values='Money', names='Партнер/Город', hole=0.5, title="📊 Деньги в логистике")
            st.plotly_chart(fig_l, use_container_width=True)
