import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- НАСТРОЙКИ СТИЛЯ (ПОД ДИЗАЙН ПРИМЕРА) ---
st.set_page_config(page_title="RBS NEON CONTROL", layout="wide")

# CSS для темной темы и свечения
st.markdown("""
<style>
    /* Фон и общий текст */
    .stApp {
        background: radial-gradient(circle at center, #0B1F3F 0%, #050C1A 100%);
        color: #E0E6ED;
        font-family: 'SF Pro Display', sans-serif;
    }
    
    /* Кнопки меню */
    [data-testid="stSidebar"] {
        background-color: #050C1A;
        border-right: 1px solid #00F2FE;
    }
    .st-dg { /* Текст в меню */
        color: #E0E6ED;
    }

    /* Крупные карточки показателей */
    [data-testid="stMetricValue"] {
        color: #00F2FE !important;
        font-size: 38px !important;
        font-weight: bold;
        text-shadow: 0 0 10px #00F2FE;
    }
    [data-testid="stMetricLabel"] {
        color: #E0E6ED !important;
        font-size: 16px !important;
    }
    .stMetric {
        background-color: rgba(10, 30, 60, 0.6);
        border: 1px solid #00F2FE;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
    }

    /* Заголовки */
    h1, h2, h3 {
        color: #FFFFFF !important;
        text-shadow: 0 0 8px #FFFFFF;
        font-weight: 300;
    }
    
    /* Таблицы */
    .stDataFrame {
        border: 1px solid #00F2FE;
        border-radius: 10px;
        background-color: rgba(10, 30, 60, 0.5);
    }

    /* Разделители */
    hr {
        border-color: #00F2FE;
    }
</style>
""", unsafe_allow_html=True)

# --- ССЫЛКИ ---
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Умная чистка денег (вытаскивает цифры из текста)
def clean_n(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Находим только цифры и точки
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(URL_SKLAD).iloc[:80, 0:17].fillna(0)
        l_r = pd.read_csv(URL_LOGISTIC).fillna(0)
        l = l_r.iloc[:, [1, 10, 11]]
        l.columns = ['Партнер/Город', 'Номера посылок', 'Обязательства']
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_all()

# --- МЕНЮ СБОКУ ---
st.sidebar.markdown("### 💎 RBS NEON COMMAND")
mode = st.sidebar.radio("ПЕРЕЙТИ В:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if mode == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 ТЕКУЩИЕ ОСТАТКИ СКЛАДА</h1>", unsafe_allow_html=True)
    if not df_s.empty:
        # Фильтры
        st.sidebar.subheader("🔍 Фильтры Склада")
        p_col, c_col = df_s.columns[1], df_s.columns[2]
        sel_p = st.sidebar.multiselect("Выберите Партнера:", sorted(df_s[p_col].unique().astype(str)))
        
        df_f = df_s.copy()
        if sel_p: df_f = df_f[df_f[p_col].astype(str).isin(sel_p)]

        # Метрики
        m1, m2, m3 = st.columns(3)
        m1.metric("КАССЫ В НАЛИЧИИ", f"{int(df_f.iloc[:, 5].apply(clean_n).sum())} шт")
        m2.metric("ФН (ВСЕГО)", f"{int(df_f.iloc[:, 6].apply(clean_n).sum() + df_f.iloc[:, 7].apply(clean_n).sum())} шт")
        m3.metric("ПОТЕНЦИАЛ ДЕНЕГ (₽)", f"{df_f.iloc[:, 13].apply(clean_n).sum():,.0f}".replace(',',' '))

        st.dataframe(df_f, use_container_width=True, hide_index=True)

        if not df_f.empty:
            fig = px.pie(df_f, values=df_f.columns[5], names=c_col, hole=0.5, 
                         title="🔵 Доли ККТ по городам")
            # Настройка цветов графика под Neon
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E6ED")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Ошибка загрузки данных!")

else:
    st.markdown("<h1>🚚 ОБЯЗАТЕЛЬСТВА И ПОСЫЛКИ</h1>", unsafe_allow_html=True)
    if not df_l.empty:
        # Фильтры логистики
        st.sidebar.subheader("🔍 Поиск и Партнеры")
        search = st.sidebar.text_input("Найти (номер или город):")
        
        df_res = df_l.copy()
        if search:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Считаем деньги (умный парсинг)
        df_res['Money'] = df_res['Обязательства'].apply(clean_n)
        total_m = df_res['Money'].sum()
        
        # Метрики логистики
        c1, c2 = st.columns(2)
        c1.metric("ОБЩИЕ ОБЯЗАТЕЛЬСТВА", f"{total_m:,.0f} ₽".replace(',',' '))
        c2.metric("ПОСЫЛОК В РАБОТЕ", len(df_res[df_res['Номера посылок'] != 0]))

        st.dataframe(df_res[['Партнер/Город', 'Номера посылок', 'Обязательства']], use_container_width=True, hide_index=True, height=500)

        # График Логистики (подсвеченный)
        if total_m > 0:
            fig_l = px.pie(df_res[df_res['Money'] > 0], values='Money', names='Партнер/Город', hole=0.5, 
                           title="📊 Деньги")
            fig_l.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E0E6ED")
            st.plotly_chart(fig_l, use_container_width=True)
        
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 СКАЧАТЬ В EXCEL", data=csv, file_name='RBS_2026.csv')
    else:
        st.error("Ошибка загрузки данных!")

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
