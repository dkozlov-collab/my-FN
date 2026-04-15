import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(layout="wide", page_title="RBS NEON ANALYTICS")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #050c1a, #0a1e3c); color: #e0e6ed; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 34px !important; font-weight: 800; text-shadow: 0 0 10px #00f2fe; }
    [data-testid="metric-container"] { background: rgba(16, 32, 64, 0.4); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: rgba(16, 32, 64, 0.6); 
        border-radius: 10px 10px 0 0; border: 1px solid #00f2fe; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #00f2fe !important; color: #050c1a !important; }
    h1 { text-align: center; text-shadow: 0 0 20px #00f2fe; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ---
U_S = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
U_L = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(U_S).iloc[:500, 0:80].fillna("")
        l = pd.read_csv(U_L).iloc[:1000, 0:80].fillna("")
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_all()

# --- БОКОВОЕ МЕНЮ (ГЛОБАЛЬНЫЕ ФИЛЬТРЫ) ---
st.sidebar.title("💎 RBS COMMAND CENTER")
st.sidebar.subheader("Глобальная Верификация")

# Собираем всех уникальных партнеров из обеих таблиц
all_partners = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Выберите партнеров (для всех вкладок):", all_partners)

# Применяем фильтр к данным
df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw

# --- ВКЛАДКИ ---
tab_dash, tab_sklad, tab_logist, tab_charts = st.tabs([
    "📊 ОБЩИЙ ДАШБОРД", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА 2026", "📈 ГРАФИКИ И АНАЛИЗ"
])

# --- 1. ДАШБОРД ---
with tab_dash:
    st.markdown("<h1>💎 ГЛОБАЛЬНЫЙ МОНИТОРИНГ</h1>", unsafe_allow_html=True)
    kkt = df_s.iloc[:, 5].apply(clean).sum()
    fn = df_s.iloc[:, 6].apply(clean).sum() + df_s.iloc[:, 7].apply(clean).sum()
    money = df_l.iloc[:, 11].apply(clean).sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("КАССЫ В НАЛИЧИИ", f"{int(kkt)} шт")
    c2.metric("ФН ОСТАТОК", f"{int(fn)} шт")
    c3.metric("ОБЯЗАТЕЛЬСТВА", f"{money:,.0f} ₽".replace(',',' '))
    
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### 🏢 Доли по партнерам (Склад)")
        fig1 = px.pie(df_s, values=df_s.columns[5], names=df_s.columns[1], hole=0.6, color_discrete_sequence=px.colors.sequential.Cyan_r)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        st.write("### 💰 Деньги в логистике")
        fig2 = px.pie(df_l, values=df_l.iloc[:, 11].apply(clean), names=df_l.columns[1], hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn_r)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- 2. СКЛАД ---
with tab_sklad:
    st.write("### 📋 Полный реестр склада (80 столбцов)")
    search_s = st.text_input("🔍 Быстрый поиск по складу:")
    if search_s:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    st.dataframe(df_s, use_container_width=True, height=600)
    # --- 3. ЛОГИСТИКА ---
with tab_logist:
    st.write("### 🚚 Бесконечный массив логистики")
    search_l = st.text_input("🔍 Поиск по номерам/получателям:")
    if search_l:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
    st.dataframe(df_l, use_container_width=True, height=600)

# --- 4. АНАЛИЗ ---
with tab_charts:
    st.write("### 📈 Детальная аналитика по городам")
    chart_type = st.segmented_control("Тип данных:", ["Кассы на складе", "Деньги в пути"])
    
    if chart_type == "Кассы на складе":
        fig_an = px.bar(df_s, x=df_s.columns[2], y=df_s.columns[5], color=df_s.columns[1], 
                        title="Распределение ККТ по городам", barmode='group')
    else:
        fig_an = px.bar(df_l, x=df_l.columns[2], y=df_l.iloc[:, 11].apply(clean), color=df_l.columns[1], 
                        title="Обязательства по регионам")
    
    fig_an.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_an, use_container_width=True)
