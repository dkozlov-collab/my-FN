import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. НАСТРОЙКА ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide", page_title="RBS BUSINESS ENGINE")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-header { font-size: 28px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px !important; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 8px; }
    .sidebar-text { font-size: 14px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗЧИК ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=10)
def load_data():
    try:
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna("")
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna("")
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_data()

# --- 3. ГЛОБАЛЬНАЯ ФИЛЬТРАЦИЯ (БОКОВАЯ ПАНЕЛЬ) ---
st.sidebar.header("⚙️ ФИЛЬТРЫ СИСТЕМЫ")

# Фильтр по Бизнес-партнерам
partners = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Бизнес-партнеры:", [x for x in partners if x not in ["", "0", "0.0"]])

# Фильтр по Городам (Отправителям/Получателям)
cities = sorted(list(set(df_s_raw.iloc[:, 2].astype(str)) | set(df_l_raw.iloc[:, 3].astype(str))))
sel_c = st.sidebar.multiselect("Города/Отправители:", [x for x in cities if x not in ["", "0"]])

# Применяем фильтры
df_s = df_s_raw.copy()
df_l = df_l_raw.copy()

if sel_p:
    df_s = df_s[df_s.iloc[:, 1].astype(str).isin(sel_p)]
    df_l = df_l[df_l.iloc[:, 1].astype(str).isin(sel_p)]
if sel_c:
    df_s = df_s[df_s.iloc[:, 2].astype(str).isin(sel_c)]
    df_l = df_l[df_l.iloc[:, 3].astype(str).isin(sel_c)]

# --- 4. ВКЛАДКИ ---
st.markdown("<div class='main-header'>RBS: УПРАВЛЕНИЕ СКЛАДОМ И ЛОГИСТИКОЙ</div>", unsafe_allow_html=True)
tab_s, tab_l, tab_a = st.tabs(["📦 СКЛАД (ОСТАТКИ)", "🚚 ЛОГИСТИКА (ОТПРАВКИ)", "📈 АНАЛИТИКА"])

with tab_s:
    st.write("### 📊 Остатки по 80 столбцам")
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with tab_l:
    st.write("### 🚛 Логистика (ТТН, Даты, Номера)")
    # Поиск внутри логистики
    search_l = st.text_input("🔍 Быстрый поиск (по № ТТН или серийнику):")
    if search_l:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

with tab_a:
    st.write("### 📊 Глобальный подсчет")
    
    # Расчеты для аналитики
    total_kkt = df_s.iloc[:, 5].apply(to_n).sum()
    total_fn = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    
    # Подсчет только по Москве (предположим, город во 2-м столбце склада)
    moscow_kkt = df_s[df_s.iloc[:, 2].astype(str).str.contains("Москва", case=False)].iloc[:, 5].apply(to_n).sum()
    
    # Отправлено (данные из логистики, 11-й столбец)
    sent_count = df_l.iloc[:, 11].apply(to_n).count() 

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ВСЕГО ККТ", f"{int(total_kkt)} шт")
    col2.metric("ВСЕГО ФН", f"{int(total_fn)} шт")
    col3.metric("ТОЛЬКО МОСКВА", f"{int(moscow_kkt)} шт")
    col4.metric("ОТПРАВЛЕНО (ТТН)", f"{int(sent_count)} ед")

    st.divider()
    
    # График остатков
    c_left, c_right = st.columns(2)
    with c_left:
        fig_s = px.bar(df_s, x=df_s.columns[1], y=df_s.columns[5], color=df_s.columns[2], title="Остатки ККТ по партнерам")
        st.plotly_chart(fig_s, use_container_width=True)
    with c_right:
        # Аналитика отправки
        fig_l = px.pie(df_l, values=df_l.iloc[:, 11].apply(to_n), names=df_l.columns[1], title="Объем логистики по партнерам (₽)")
        st.plotly_chart(fig_l, use_container_width=True)
