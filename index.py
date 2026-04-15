import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. НАСТРОЙКА ВИДА ---
st.set_page_config(layout="wide", page_title="RBS NEON 2026")

# Ручной CSS для темной темы
st.markdown("""
<style>
    .stApp { background-color: #050c1a; color: #e0e6ed; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 32px !important; font-weight: bold; }
    [data-testid="metric-container"] { background: #0a1e3c; border: 1px solid #00f2fe; border-radius: 10px; padding: 10px; }
    h1 { text-align: center; color: #00f2fe; text-transform: uppercase; }
    .stTabs [data-baseweb="tab"] { color: white; border: 1px solid #00f2fe; border-radius: 5px; margin: 2px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ССЫЛКИ НА ТАБЛИЦЫ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# --- 3. ЗАГРУЗКА (РУЧНАЯ) ---
@st.cache_data(ttl=5)
def get_data():
    # Склад: берем первые 80 столбцов
    s = pd.read_csv(S_URL).iloc[:500, 0:80].fillna("")
    # Логистика: берем до 1000 строк
    l = pd.read_csv(L_URL).iloc[:1000, 0:80].fillna("")
    return s, l

df_s_raw, df_l_raw = get_data()

# --- 4. ФИЛЬТРАЦИЯ (РУЧНАЯ) ---
st.sidebar.title("💎 RBS ФИЛЬТР")
p_list = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Выберите партнера:", [x for x in p_list if x not in ["", "0", "0.0"]])

# Применяем фильтр вручную
df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_s_raw
df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_l_raw

# --- 5. ВКЛАДКИ ---
t1, t2, t3 = st.tabs(["📊 ГЛАВНАЯ", "📦 СКЛАД", "🚚 ЛОГИСТИКА"])

with t1:
    st.markdown("<h1>RBS GLOBAL MONITOR</h1>", unsafe_allow_html=True)
    
    # Ручной расчет сумм
    def parse_n(val):
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0

    kkt = df_s.iloc[:, 5].apply(parse_n).sum()
    fn = df_s.iloc[:, 6].apply(parse_n).sum() + df_s.iloc[:, 7].apply(parse_n).sum()
    money = df_l.iloc[:, 11].apply(parse_n).sum()

    # Вывод карточек
    c1, c2, c3 = st.columns(3)
    c1.metric("КАССЫ", f"{int(kkt)} шт")
    c2.metric("ФН", f"{int(fn)} шт")
    # Форматируем вручную, чтобы не было ValueError
    m_str = f"{int(money):,}".replace(",", " ")
    c3.metric("ДЕНЬГИ", f"{m_str} ₽")

    # Простой график
    if kkt > 0:
        fig = px.pie(df_s, values=df_s.columns[5], names=df_s.columns[1], hole=0.5, title="Доли ККТ")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

with t2:
    st.write("### 📋 Таблица Склада (80 столбцов)")
    st.dataframe(df_s, use_container_width=True)

with t3:
    st.write("### 🚚 Таблица Логистики")
    find = st.text_input("Поиск по номеру:")
    if find:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(find, case=False).any(), axis=1)]
    st.dataframe(df_l, use_container_width=True)
