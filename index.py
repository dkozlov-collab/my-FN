import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- НАСТРОЙКИ СТИЛЯ (NEON DESIGN) ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL ANALYTICS")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #050c1a, #0a1e3c); color: #e0e6ed; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 36px !important; font-weight: 800; text-shadow: 0 0 10px #00f2fe; }
    [data-testid="metric-container"] { background: rgba(16, 32, 64, 0.5); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; }
    .stDataFrame { border: 1px solid #00f2fe; border-radius: 10px; background: #050c1a; }
    h1 { text-align: center; color: #ffffff; text-transform: uppercase; letter-spacing: 3px; text-shadow: 0 0 15px #00f2fe; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
U_S = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
U_L = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Очистка данных (решает TypeError)
def clean(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data(u, c=80, r=1000):
    try: return pd.read_csv(u).iloc[:r, 0:c].fillna("")
    except: return pd.DataFrame()

# --- ЛОГИКА ПРИЛОЖЕНИЯ ---
st.sidebar.title("💎 RBS COMMAND")
m = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД (80 СТОЛБЦОВ)", "🚚 ЛОГИСТИКА 2026"])

if m == "📦 СКЛАД (80 СТОЛБЦОВ)":
    st.markdown("<h1>📦 АНАЛИТИКА СКЛАДА</h1>", unsafe_allow_html=True)
    df = load_data(U_S, 80, 500)
    
    # Фильтрация по партнерам и городам
    st.sidebar.subheader("🔍 ВЕРИФИКАЦИЯ ПАРТНЕРОВ")
    f_p = st.sidebar.multiselect("Партнеры:", sorted(df.iloc[:, 1].unique().astype(str)))
    f_c = st.sidebar.multiselect("Города:", sorted(df.iloc[:, 2].unique().astype(str)))
    
    if f_p: df = df[df.iloc[:, 1].astype(str).isin(f_p)]
    if f_c: df = df[df.iloc[:, 2].astype(str).isin(f_c)]

    # Итоги (Кассы-ст.6, ФН-ст.7,8)
    kkt = df.iloc[:, 5].apply(clean).sum()
    fn = df.iloc[:, 6].apply(clean).sum() + df.iloc[:, 7].apply(clean).sum()

    c1, c2 = st.columns(2)
    c1.metric("КАССЫ ПО ФИЛЬТРУ", f"{int(kkt)} шт")
    c2.metric("ФН ПО ФИЛЬТРУ", f"{int(fn)} шт")
    
    st.dataframe(df, use_container_width=True)
    
    if kkt > 0:
        fig = px.pie(df, values=df.columns[5], names=df.columns[2], hole=0.6, color_discrete_sequence=px.colors.sequential.Cyan_r)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА: БЕСКОНЕЧНЫЙ МАССИВ</h1>", unsafe_allow_html=True)
    df = load_data(U_L, 80, 1000)
    
    # Фильтрация логистики
    st.sidebar.subheader("🔍 ВЕРИФИКАЦИЯ ГРУЗОВ")
    search = st.sidebar.text_input("Поиск (номер/город/имя):")
    f_p_l = st.sidebar.multiselect("Отправитель:", sorted(df.iloc[:, 1].unique().astype(str)))
    
    if f_p_l: df = df[df.iloc[:, 1].astype(str).isin(f_p_l)]
    if search: df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

    # Деньги (ст. L - индекс 11)
    money = df.iloc[:, 11].apply(clean).sum()
    
    col1, col2 = st.columns(2)
    col1.metric("ОБЯЗАТЕЛЬСТВА", f"{money:,.0f} ₽".replace(',',' '))
    col2.metric("ЗАПИСЕЙ В РАБОТЕ", len(df))

    st.dataframe(df, use_container_width=True, height=500)

    if money > 0:
        fig_l = px.pie(df, values=df.iloc[:, 11].apply(clean), names=df.columns[1], hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn_r)
        fig_l.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_l, use_container_width=True)
