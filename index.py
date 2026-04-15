import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. КОНФИГУРАЦИЯ И СВЕТЛЫЙ СТИЛЬ ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL SYSTEM 2026")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #1C1C1E; }
    [data-testid="stMetricValue"] { color: #0047AB !important; font-size: 32px !important; font-weight: 800; }
    [data-testid="metric-container"] { 
        background-color: #F2F2F7; 
        border: 1px solid #D1D1D6; 
        border-radius: 12px; 
        padding: 20px;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #F2F2F7; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #1C1C1E; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF !important; border-radius: 7px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    h1 { color: #000000; text-align: center; font-weight: 900; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ДВИЖОК ЗАГРУЗКИ ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(v):
    try:
        res = re.findall(r'\d+', str(v).replace(' ',''))
        return float(res[0]) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def fetch_data():
    try:
        # Склад 80 столбцов / Логистика 1000 строк
        s_data = pd.read_csv(S_URL).iloc[:500, 0:80].fillna("")
        l_data = pd.read_csv(L_URL).iloc[:1000, 0:80].fillna("")
        return s_data, l_data
    except Exception as e:
        st.error(f"Доступ заблокирован! Опубликуй таблицы в интернете (CSV). Ошибка: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = fetch_data()

# --- 3. СКВОЗНАЯ СОРТИРОВКА И ФИЛЬТРАЦИЯ ---
st.sidebar.header("⚙️ ПАНЕЛЬ УПРАВЛЕНИЯ")
p_all = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("ВЕРИФИКАЦИЯ ПАРТНЕРОВ (АБ и др.):", [x for x in p_all if x not in ["", "0", "0.0"]])

# Применяем фильтр к обоим источникам одновременно
df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_s_raw
df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_l_raw

# --- 4. ФУНКЦИОНАЛЬНЫЕ ВКЛАДКИ ---
t1, t2, t3, t4 = st.tabs(["💎 ДАШБОРД", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА", "📊 АНАЛИТИКА"])

with t1:
    st.markdown("<h1>RBS GLOBAL MONITORING</h1>", unsafe_allow_html=True)
    
    # Расчет ключевых остатков
    kkt_val = df_s.iloc[:, 5].apply(clean_num).sum()
    fn_val = df_s.iloc[:, 6].apply(clean_num).sum() + df_s.iloc[:, 7].apply(clean_num).sum()
    cash_val = df_l.iloc[:, 11].apply(clean_num).sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ККТ В НАЛИЧИИ", f"{int(kkt_val)} шт")
    c2.metric("ФН В НАЛИЧИИ", f"{int(fn_val)} шт")
    # Красивый вывод денег
    money_fmt = "{:,.0f}".format(cash_val).replace(",", " ")
    c3.metric("ОБЯЗАТЕЛЬСТВА", f"{money_fmt} ₽")
    
    st.divider()
    
    # Краткий обзор
    col_pie_1, col_pie_2 = st.columns(2)
    with col_pie_1:
        st.plotly_chart(px.pie(df_s, values=df_s.columns[5], names=df_s.columns[1], title="Доли ККТ по партнерам", hole=0.5), use_container_width=True)
    with col_pie_2:
        st.plotly_chart(px.pie(df_l, values=df_l.iloc[:, 11].apply(clean_num), names=df_l.columns[1], title="Доли ₽ в логистике", hole=0.5), use_container_width=True)

with t2:
    st.write("### 📦 Интерактивный Склад (80 столбцов)")
    # Кликабельная таблица с поиском и сортировкой
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Логистика и Потоки данных")
    search_q = st.text_input("🔍 Глобальный поиск (город, серийник, имя):")
    if search_q:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

with t4:
    st.write("### 📉 Анализ движения оборудования")
    # График списания / остатков по городам
    df_city = df_s.copy()
    df_city['KKT_COUNT'] = df_city.iloc[:, 5].apply(clean_num)
    fig_bar = px.bar(df_city, x=df_city.columns[2], y='KKT_COUNT', color=df_city.columns[1], title="Распределение касс по городам")
    st.plotly_chart(fig_bar, use_container_width=True)
