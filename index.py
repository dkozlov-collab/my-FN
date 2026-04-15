import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- НАСТРОЙКИ СТИЛЯ (NEON DARK) ---
st.set_page_config(layout="wide", page_title="RBS NEON SYSTEM")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #050c1a, #0a1e3c); color: #e0e6ed; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 32px !important; font-weight: 800; text-shadow: 0 0 10px #00f2fe; }
    [data-testid="metric-container"] { background: rgba(16, 32, 64, 0.4); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; background-color: rgba(16, 32, 64, 0.6); 
        border-radius: 8px 8px 0 0; border: 1px solid #00f2fe; color: white; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00f2fe !important; color: #050c1a !important; font-weight: bold; }
    h1 { text-align: center; text-shadow: 0 0 20px #00f2fe; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# --- БЕЗОПАСНЫЕ ФУНКЦИИ (БЕЗ ОШИБОК) ---
def to_n(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

# --- ЗАГРУЗКА ДАННЫХ ---
U_S = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
U_L = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(U_S).iloc[:500, 0:80].fillna("")
        l = pd.read_csv(U_L).iloc[:1000, 0:80].fillna("")
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_all()

# --- САЙДБАР ---
st.sidebar.title("💎 RBS COMMAND")
p_all = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Выберите партнеров:", [x for x in p_all if x not in ["0.0", "", "0"]])

df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_s_raw
df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_l_raw

# --- ВКЛАДКИ ---
t1, t2, t3, t4 = st.tabs(["📊 ДАШБОРД", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА", "📈 АНАЛИТИКА"])

with t1:
    st.markdown("<h1>💎 ГЛОБАЛЬНЫЙ МОНИТОРИНГ</h1>", unsafe_allow_html=True)
    kkt = df_s.iloc[:, 5].apply(to_n).sum()
    fn = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    money = df_l.iloc[:, 11].apply(to_n).sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("КАССЫ В НАЛИЧИИ", f"{int(kkt)} шт")
    c2.metric("ФН ОСТАТОК", f"{int(fn)} шт")
    
    # ВОТ ЗДЕСЬ ИСПРАВЛЕНО: используем формат с пробелом вместо .replace
    c3.metric("ОБЯЗАТЕЛЬСТВА", f"{money:,.0f} ₽".replace(",", " "))
    
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.pie(df_s, values=df_s.columns[5], names=df_s.columns[1], hole=0.6, title="Доли ККТ")
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.pie(df_l, values=df_l.iloc[:, 11].apply(to_n), names=df_l.columns[1], hole=0.6, title="Доли ₽")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

with t2:
    st.write("### 📦 Полный реестр склада")
    st.dataframe(df_s, use_container_width=True, height=600)

with t3:
    st.write("### 🚚 Логистика и посылки")
    search = st.text_input("🔍 Быстрый поиск:")
    df_l_f = df_l.copy()
    if search:
        df_l_f = df_l_f[df_l_f.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df_l_f, use_container_width=True, height=600)
    with t4:
    st.write("### 📈 Аналитика по регионам")
    if not df_s.empty:
        df_city = df_s.copy()
        df_city['KKT_VAL'] = df_city.iloc[:, 5].apply(to_n)
        city_sum = df_city.groupby(df_city.columns[2])['KKT_VAL'].sum().reset_index()
        fig_bar = px.bar(city_sum, x=city_sum.columns[0], y='KKT_VAL', title="ККТ по городам", color_discrete_sequence=['#00f2fe'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)
