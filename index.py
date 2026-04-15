import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка Pocophone
st.set_page_config(page_title="RBS 2026: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Чистим цифры (чтобы буквы в ячейках не ломали расчеты)
def parse_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        res = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
        return float(res) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_full_data(url):
    try:
        # Читаем всё полотно до 80 столбца
        df = pd.read_csv(url).iloc[:100, 0:80].fillna("")
        return df
    except: return pd.DataFrame()

# --- ГЛАВНОЕ МЕНЮ ---
st.sidebar.title("💎 RBS SYSTEM")
choice = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if choice == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 ПОЛНЫЙ РЕЕСТР СКЛАДА</h1>", unsafe_allow_html=True)
    df_s = load_full_data(URL_SKLAD)
    
    if not df_s.empty:
        # Фильтры (Столбцы B и C)
        st.sidebar.subheader("🔍 Фильтры Склада")
        all_p = ["Все"] + sorted(df_s.iloc[:, 1].unique().astype(str).tolist())
        sel_p = st.sidebar.selectbox("Партнер:", all_p)
        
        df_f = df_s.copy()
        if sel_p != "Все":
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_p]

        # Итоги (Кассы - 6 ст, ФН - 7,8 ст)
        kkt = df_f.iloc[:, 5].apply(parse_num).sum()
        fn = df_f.iloc[:, 6].apply(parse_num).sum() + df_f.iloc[:, 7].apply(parse_num).sum()

        c1, c2 = st.columns(2)
        c1.metric("КАССЫ (ШТ)", f"{int(kkt)}")
        c2.metric("ФН (ШТ)", f"{int(fn)}")

        st.dataframe(df_f, use_container_width=True)
        
        if kkt > 0:
            fig = px.pie(df_f, values=df_f.columns[5], names=df_f.columns[2], hole=0.4, title="Доли ККТ")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ПОЛНЫЙ МАССИВ ЛОГИСТИКИ</h1>", unsafe_allow_html=True)
    df_l = load_full_data(URL_LOGISTIC)
    
    if not df_l.empty:
        st.sidebar.subheader("🔍 Фильтры Логистики")
        # Партнер в новой таблице тоже во 2-м столбце (B)
        l_p = ["Все"] + sorted(df_l.iloc[:, 1].unique().astype(str).tolist())
        sel_lp = st.sidebar.selectbox("Партнер:", l_p)
        search = st.sidebar.text_input("Поиск по номеру/тексту:")

        df_res = df_l.copy()
        if sel_lp != "Все":
            df_res = df_res[df_res.iloc[:, 1].astype(str) == sel_lp]
        if search:
            df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Деньги (в новой таблице это столбец L - индекс 11)
        money_col = df_res.iloc[:, 11].apply(parse_num)
        total_money = money_col.sum()

        col1, col2 = st.columns(2)
        col1.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{total_money:,.0f} ₽".replace(',', ' '))
        col2.metric("ВСЕГО СТРОК", len(df_res))

        st.write("### 📋 Полная информация (Все столбцы)")
        st.dataframe(df_res, use_container_width=True)

        if total_money > 0:
            # График по столбцу L и партнерам из столбца B
            fig_l = px.pie(names=df_res.iloc[:, 1], values=money_col, hole=0.4, title="Деньги по партнерам")
            st.plotly_chart(fig_l, use_container_width=True)
            
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Скачать весь массив CSV", csv, "RBS_Full_Logistics.csv", "text/csv")
