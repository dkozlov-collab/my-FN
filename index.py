import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под широкий экран (Pocophone/ПК)
st.set_page_config(page_title="RBS: Полный Массив 2026", layout="wide")

# Стиль
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ (CSV экспорт)
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Функция очистки для расчетов (чтобы буквы не мешали считать сумму)
def parse_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_sklad():
    try:
        # Читаем до 80 столбца (A:CB)
        df = pd.read_csv(URL_SKLAD).iloc[:100, 0:80].fillna("")
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=5)
def load_logistics():
    try:
        df = pd.read_csv(URL_LOGISTIC).fillna("")
        # Колонки B(1), K(10), L(11)
        df_sub = df.iloc[:, [1, 10, 11]]
        df_sub.columns = ['Партнер/Город', 'Трек-номера', 'Обязательства']
        return df_sub
    except: return pd.DataFrame()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS УПРАВЛЕНИЕ")
choice = st.sidebar.radio("ПЕРЕЙТИ В РАЗДЕЛ:", ["📦 СКЛАД (80 столбцов)", "🚚 ЛОГИСТИКА 2026"])

if choice == "📦 СКЛАД (80 столбцов)":
    st.markdown("<h1>📦 СКЛАД: ПОЛНЫЙ РЕЕСТР</h1>", unsafe_allow_html=True)
    df_s = load_sklad()
    
    if not df_s.empty:
        # Фильтры
        st.sidebar.subheader("🔍 Фильтрация")
        all_partners = ["Все"] + sorted(df_s.iloc[:, 1].unique().astype(str).tolist())
        sel_p = st.sidebar.selectbox("Выбор партнера:", all_partners)
        
        df_f = df_s.copy()
        if sel_p != "Все":
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_p]

        # Расчет показателей (Кассы - 6 ст., ФН - 7 и 8 ст.)
        kkt = df_f.iloc[:, 5].apply(parse_num).sum()
        fn = df_f.iloc[:, 6].apply(parse_num).sum() + df_f.iloc[:, 7].apply(parse_num).sum()

        col1, col2 = st.columns(2)
        col1.metric("КАССЫ В НАЛИЧИИ", f"{int(kkt)} шт")
        col2.metric("ОСТАТОК ФН", f"{int(fn)} шт")

        st.write("### 📋 Весь массив данных (текст + цифры)")
        st.dataframe(df_f, use_container_width=True)

        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], hole=0.4, title="Распределение касс")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Данные склада не загружены!")

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА: ПОСЫЛКИ 2026</h1>", unsafe_allow_html=True)
    df_l = load_logistics()
    
    if not df_l.empty:
        st.sidebar.subheader("🔍 Фильтры Логистики")
        l_partners = ["Все"] + sorted(df_l['Партнер/Город'].unique().astype(str).tolist())
        sel_lp = st.sidebar.selectbox("Партнер:", l_partners)
        search = st.sidebar.text_input("Поиск по номеру:")

        df_res = df_l.copy()
        if sel_lp != "Все":
            df_res = df_res[df_res['Партнер/Город'].astype(str) == sel_lp]
        if search:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Деньги
        df_res['Sum'] = df_res['Обязательства'].apply(parse_num)
        total_m = df_res['Sum'].sum()

        c1, c2 = st.columns(2)
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_money:,.0f} ₽".replace(',', ' '))
        c2.metric("ОТПРАВЛЕНО", len(df_res[df_res['Трек-номера'] != ""]))
        st.dataframe(df_res[['Партнер/Город', 'Трек-номера', 'Обязательства']], use_container_width=True, height=500)

        if total_m > 0:
            fig_l = px.pie(df_res[df_res['Sum']>0], values='Sum', names='Партнер/Город', hole=0.4, title="Обязательства по городам")
            st.plotly_chart(fig_l, use_container_width=True)
