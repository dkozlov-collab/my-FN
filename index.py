import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# УМНАЯ ЧИСТКА ЦИФР (решает проблему 0 руб и TypeError)
def clean_money(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Оставляем только цифры и точки
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        # Грузим склад
        s = pd.read_csv(URL_SKLAD).iloc[:80, 0:17].fillna(0)
        # Грузим логистику (B, K, L)
        l_raw = pd.read_csv(URL_LOGISTIC).fillna(0)
        l = l_raw.iloc[:, [1, 10, 11]]
        l.columns = ['Партнер', 'Номера', 'Обязательства']
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS SYSTEM")
mode = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД", "🚚 ЛОГИСТИКА 2026"])

df_s, df_l = load_all()

if mode == "📦 СКЛАД":
    st.markdown("<h1>📦 СКЛАД И ОСТАТКИ</h1>", unsafe_allow_html=True)
    if not df_s.empty:
        # Поиск и фильтр
        p_col, c_col = df_s.columns[1], df_s.columns[2]
        sel_p = st.sidebar.multiselect("Партнер:", sorted(df_s[p_col].unique().astype(str)))
        
        df_f = df_s.copy()
        if sel_p: df_f = df_f[df_f[p_col].astype(str).isin(sel_p)]
        
        # Метрики (чистим перед суммой)
        kkt = df_f.iloc[:, 5].apply(clean_money).sum()
        fn = df_f.iloc[:, 6].apply(clean_money).sum() + df_f.iloc[:, 7].apply(clean_money).sum()
        
        c1, c2 = st.columns(2)
        c1.metric("ККТ (ШТ)", f"{int(kkt)}")
        c2.metric("ФН (ШТ)", f"{int(fn)}")
        
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        
        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=c_col, hole=0.5, title="🔵 Доли ККТ")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА 2026</h1>", unsafe_allow_html=True)
    if not df_l.empty:
        search = st.sidebar.text_input("🔍 Поиск по номеру:")
        sel_lp = st.sidebar.multiselect("Партнер:", sorted(df_l['Партнер'].unique().astype(str)))
        
        df_res = df_l.copy()
        if sel_lp: df_res = df_res[df_res['Партнер'].astype(str).isin(sel_lp)]
        if search: df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        # Считаем деньги (умный парсинг решает проблему 0 руб)
        df_res['Money'] = df_res['Обязательства'].apply(clean_money)
        total_m = df_res['Money'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("ОБЯЗАТЕЛЬСТВА", f"{total_m:,.0f} ₽".replace(',', ' '))
        c2.metric("ПОСЫЛКИ", len(df_res[df_res['Номера'] != 0]))
        
        st.dataframe(df_res[['Партнер', 'Номера', 'Обязательства']], use_container_width=True, hide_index=True)
        
        if total_m > 0:
            fig_l = px.pie(df_res[df_res['Money']>0], values='Money', names='Партнер', hole=0.5, title="📊 Деньги")
            st.plotly_chart(fig_l, use_container_width=True)
