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
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .section-box { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border: 2px solid #007BFF; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- ИНСТРУМЕНТЫ ---
def extract_money(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0
    except: return 0

@st.cache_data(ttl=5)
def get_data(url, limit_cols=None):
    try:
        df = pd.read_csv(url).fillna(0)
        if limit_cols: df = df.iloc[:80, 0:limit_cols]
        return df
    except: return pd.DataFrame()

# --- ПАПКА 1: СКЛАД ---
def run_sklad():
    st.markdown("<h1>📦 СКЛАД И ОСТАТКИ</h1>", unsafe_allow_html=True)
    df = get_data(URL_SKLAD, 17)
    
    if not df.empty:
        # Фильтры в сайдбаре
        st.sidebar.subheader("⚙️ Настройка Склада")
        partner_col = df.columns[1]
        city_col = df.columns[2]
        
        sel_p = st.sidebar.multiselect("Выберите Партнера:", sorted(df[partner_col].unique().tolist()))
        sel_c = st.sidebar.multiselect("Выберите Город:", sorted(df[city_col].unique().tolist()))

        df_f = df.copy()
        if sel_p: df_f = df_f[df_f[partner_col].isin(sel_p)]
        if sel_c: df_f = df_f[df_f[city_col].isin(sel_c)]

        # Метрики
        m1, m2, m3 = st.columns(3)
        m1.metric("ККТ (ШТ)", int(df_f.iloc[:, 5].sum()))
        m2.metric("ФН (ШТ)", int(df_f.iloc[:, 6].sum() + df_f.iloc[:, 7].sum()))
        m3.metric("ДЕНЬГИ (₽)", f"{df_f.iloc[:, 13].apply(extract_money).sum():,.0f}".replace(',', ' '))

        # Таблица
        st.dataframe(df_f, use_container_width=True)

        # График
        if not df_f.empty:
            fig = px.pie(df_f, values=df_f.columns[5], names=city_col, hole=0.5, title="🔵 Доли ККТ по городам")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Нет данных склада!")

# --- ПАПКА 2: ЛОГИСТИКА 2026 ---
def run_logistics():
    st.markdown("<h1>🚚 ЛОГИСТИКА 2026</h1>", unsafe_allow_html=True)
    df_raw = get_data(URL_LOGISTIC)
    
    if not df_raw.empty:
        # Столбцы B(1), K(10), L(11)
        df = df_raw.iloc[:, [1, 10, 11]].copy()
        df.columns = ['Партнер / Город', 'Номера посылок', 'Обязательства']
        df['Money'] = df['Обязательства'].apply(extract_money)

        # Фильтры
        st.sidebar.subheader("⚙️ Настройка Логистики")
        search = st.sidebar.text_input("🔍 Поиск (номер/город):")
        sel_lp = st.sidebar.multiselect("Фильтр по Партнеру:", sorted(df['Партнер / Город'].unique().tolist()))

        df_l = df.copy()
        if sel_lp: df_l = df_l[df_l['Партнер / Город'].isin(sel_lp)]
        if search: df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Метрики
        c1, c2 = st.columns(2)
        total = df_l['Money'].sum()
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total:,.0f} ₽".replace(',', ' '))
        c2.metric("ПОСЫЛОК В РАБОТЕ", len(df_l[df_l['Номера посылок'] != 0]))

        # Таблица
        st.dataframe(df_l[['Партнер / Город', 'Номера посылок', 'Обязательства']], use_container_width=True, height=400)
        # График Логистики
        if total > 0:
            fig_l = px.pie(df_l[df_l['Money'] > 0], values='Money', names='Партнер / Город', 
                           hole=0.5, title="📊 Распределение обязательств (₽)")
            st.plotly_chart(fig_l, use_container_width=True)
        
        # Кнопка Excel
        csv = df_l.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Скачать Логистику в Excel", data=csv, file_name='RBS_Logistics_2026.csv')
    else:
        st.error("Нет данных логистики!")

# --- МЕНЮ ---
st.sidebar.title("💎 RBS SYSTEM")
choice = st.sidebar.radio("РАЗДЕЛ:", ["📦 Склад", "🚚 Логистика 2026"])

if choice == "📦 Склад":
    run_sklad()
else:
    run_logistics()
