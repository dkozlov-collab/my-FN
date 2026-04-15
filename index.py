import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальное управление", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1, h2 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def extract_money(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        # Вытаскиваем только цифры и точки
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0
    except: return 0

@st.cache_data(ttl=5)
def load_all_data():
    try:
        df_s = pd.read_csv(URL_SKLAD).iloc[:80, 0:17].fillna(0)
        df_l_raw = pd.read_csv(URL_LOGISTIC).fillna(0)
        df_l = df_l_raw.iloc[:, [1, 10, 11]]
        df_l.columns = ['Партнер/Город', 'Номера посылок', 'Обязательства']
        return df_s, df_l
    except: return pd.DataFrame(), pd.DataFrame()

st.sidebar.title("💎 RBS SYSTEM 2026")
mode = st.sidebar.radio("ВЫБЕРИТЕ РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

df_s, df_l = load_all_data()

if mode == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 СКЛАД И ОСТАТКИ ФН</h1>", unsafe_allow_html=True)
    if not df_s.empty:
        # Фильтры склада
        st.sidebar.subheader("⚙️ Фильтры Склада")
        p_col, c_col = df_s.columns[1], df_s.columns[2]
        sel_p = st.sidebar.multiselect("Выберите Партнера:", sorted(df_s[p_col].unique().astype(str)))
        sel_c = st.sidebar.multiselect("Выберите Город:", sorted(df_s[c_col].unique().astype(str)))

        df_f = df_s.copy()
        if sel_p: df_f = df_f[df_f[p_col].astype(str).isin(sel_p)]
        if sel_c: df_f = df_f[df_f[c_col].astype(str).isin(sel_c)]

        # Метрики
        m1, m2 = st.columns(2)
        m1.metric("ККТ В НАЛИЧИИ", f"{int(df_f.iloc[:, 5].sum())} шт")
        m2.metric("ФН (ВСЕГО)", f"{int(df_f.iloc[:, 6].sum() + df_f.iloc[:, 7].sum())} шт")

        st.dataframe(df_f, use_container_width=True, hide_index=True)

        if not df_f.empty:
            fig = px.pie(df_f, values=df_f.columns[5], names=c_col, hole=0.5, title="🔵 Доли ККТ по городам")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Данные склада не найдены!")

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА И ПОСЫЛКИ 2026</h1>", unsafe_allow_html=True)
    if not df_l.empty:
        # Фильтры логистики
        st.sidebar.subheader("⚙️ Фильтры Логистики")
        search = st.sidebar.text_input("🔍 Поиск (номер/город):")
        sel_lp = st.sidebar.multiselect("Фильтр по Партнеру:", sorted(df_l['Партнер/Город'].unique().astype(str)))

        df_res = df_l.copy()
        if sel_lp: df_res = df_res[df_res['Партнер/Город'].astype(str).isin(sel_lp)]
        if search: df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Метрики логистики с умным подсчетом денег
        df_res['Money'] = df_res['Обязательства'].apply(extract_money)
        total_m = df_res['Money'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_m:,.0f} ₽".replace(',', ' '))
        c2.metric("АКТИВНЫХ ПОСЫЛОК", len(df_res[df_res['Номера посылок'] != 0]))

        st.dataframe(df_res[['Партнер/Город', 'Номера посылок', 'Обязательства']], use_container_width=True, hide_index=True, height=500)
        if total_m > 0:
            fig_l = px.pie(df_res[df_res['Money'] > 0], values='Money', names='Партнер/Город', hole=0.5, title="📊 Распределение денег (₽)")
            st.plotly_chart(fig_l, use_container_width=True)
        
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Скачать Логистику в Excel", data=csv, file_name='RBS_Logistics_2026.csv')
    else:
        st.error("Данные логистики не найдены!")
