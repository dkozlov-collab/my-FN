import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка под широкий экран (Pocophone/ПК)
st.set_page_config(page_title="RBS: Глобальный Массив 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 26px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .alarm-box { background-color: #FFEBEE; padding: 15px; border-radius: 10px; border-left: 5px solid #FF5252; color: #B71C1C; font-weight: bold; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ (Убедись, что в Google Таблице включена публикация в CSV)
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Функция для вытаскивания цифр из любого текста (чтобы буквы не мешали сумме)
def clean_val(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data(url):
    try:
        # ЗАХВАТ ДО 80 СТОЛБЦА (0:80)
        df = pd.read_csv(url).iloc[:100, 0:80].fillna("")
        return df
    except: return pd.DataFrame()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS COMMAND")
choice = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД (80 СТОЛБЦОВ)", "🚚 ЛОГИСТИКА 2026"])

if choice == "📦 СКЛАД (80 СТОЛБЦОВ)":
    st.markdown("<h1>📦 ПОЛНЫЙ МАССИВ СКЛАДА</h1>", unsafe_allow_html=True)
    df_s = load_data(URL_SKLAD)
    
    if not df_s.empty:
        # ФИЛЬТРЫ (по партнерам и городам)
        st.sidebar.subheader("🔍 Фильтрация")
        p_list = ["Все"] + sorted(df_s.iloc[:, 1].unique().astype(str).tolist())
        c_list = ["Все"] + sorted(df_s.iloc[:, 2].unique().astype(str).tolist())
        
        sel_p = st.sidebar.selectbox("Выберите партнера:", p_list)
        sel_c = st.sidebar.selectbox("Выберите город:", c_list)

        df_f = df_s.copy()
        if sel_p != "Все": df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_p]
        if sel_c != "Все": df_f = df_f[df_f.iloc[:, 2].astype(str) == sel_c]

        # ИТОГИ (Кассы - 6 ст., ФН - 7,8 ст.)
        kkt = df_f.iloc[:, 5].apply(clean_val).sum()
        fn = df_f.iloc[:, 6].apply(clean_val).sum() + df_f.iloc[:, 7].apply(clean_val).sum()

        # ТРЕВОГИ
        if kkt < 5:
            st.markdown(f"<div class='alarm-box'>⚠️ ВНИМАНИЕ: Касс осталось мало ({int(kkt)} шт)!</div>", unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("КАССЫ В НАЛИЧИИ", f"{int(kkt)} шт")
        m2.metric("ФН ОСТАТОК (ВСЕГО)", f"{int(fn)} шт")

        st.write("### 📋 Таблица (можно листать вправо до 80 столбца)")
        st.dataframe(df_f, use_container_width=True)

        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], hole=0.5, title="Доли ККТ по точкам")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА: ПОЛНЫЙ МАССИВ</h1>", unsafe_allow_html=True)
    df_l = load_data(URL_LOGISTIC)
    
    if not df_l.empty:
        st.sidebar.subheader("🔍 Поиск и фильтры")
        search = st.sidebar.text_input("Поиск (номер/получатель/город):")
        
        df_res = df_l.copy()
        if search:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # ДЕНЬГИ (Столбец L - 11 индекс)
        money = df_res.iloc[:, 11].apply(clean_val).sum()
        
        c1, c2 = st.columns(2)
        c1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{money:,.0f} ₽".replace(',', ' '))
        c2.metric("ВСЕГО СТРОК", len(df_res))
        st.write("### 📋 Данные логистики (80 столбцов)")
        st.dataframe(df_res, use_container_width=True, height=500)
        
        if money > 0:
            fig_l = px.pie(df_res, values=df_res.iloc[:, 11].apply(clean_val), names=df_res.columns[1], hole=0.5, title="Деньги по партнерам")
            st.plotly_chart(fig_l, use_container_width=True)
