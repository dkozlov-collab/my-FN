import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Настройка экрана под Pocophone
st.set_page_config(page_title="RBS: Глобальный Контроль", layout="wide")

# Стиль и цветовая индикация тревог
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    .alarm-low { background-color: #FFEBEE; padding: 10px; border-radius: 10px; border-left: 5px solid #FF5252; color: #B71C1C; margin-bottom: 10px; }
    .alarm-ok { background-color: #E8F5E9; padding: 10px; border-radius: 10px; border-left: 5px solid #4CAF50; color: #1B5E20; margin-bottom: 10px; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ (A:CB до 80 столбца)
URL_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_LOGISTIC = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0.0
        # Находим ПЕРВОЕ число в строке (игнорируем текст "загрузила", "шт" и т.д.)
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data():
    try:
        s = pd.read_csv(URL_SKLAD).iloc[:100, 0:80].fillna("")
        l = pd.read_csv(URL_LOGISTIC).iloc[:100, 0:80].fillna("")
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_data()

# --- МЕНЮ ---
st.sidebar.title("💎 RBS COMMAND")
mode = st.sidebar.radio("РАЗДЕЛ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

if mode == "📦 СКЛАД И ОСТАТКИ":
    st.markdown("<h1>📦 СКЛАД: ФИЛЬТРАЦИЯ И ТРЕВОГИ</h1>", unsafe_allow_html=True)
    
    # ФИЛЬТРЫ СКЛАДА
    st.sidebar.subheader("🔍 Фильтры")
    p_col = df_s.columns[1] # Партнер
    c_col = df_s.columns[2] # Город
    
    sel_p = st.sidebar.multiselect("Партнеры:", sorted(df_s[p_col].unique().astype(str)))
    sel_c = st.sidebar.multiselect("Города:", sorted(df_s[c_col].unique().astype(str)))

    df_f = df_s.copy()
    if sel_p: df_f = df_f[df_f[p_col].astype(str).isin(sel_p)]
    if sel_c: df_f = df_f[df_f[c_col].astype(str).isin(sel_c)]

    # ТРЕВОГИ (Alerts)
    kkt = df_f.iloc[:, 5].apply(clean_num).sum()
    fn_total = df_f.iloc[:, 6].apply(clean_num).sum() + df_f.iloc[:, 7].apply(clean_num).sum()

    st.subheader("🚨 Состояние запасов:")
    if kkt < 5:
        st.markdown(f"<div class='alarm-low'>⚠️ КРИТИЧЕСКИЙ ОСТАТОК ККТ: {int(kkt)} шт! Срочно пополни склад.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alarm-ok'>✅ ККТ в норме: {int(kkt)} шт.</div>", unsafe_allow_html=True)
    
    if fn_total < 10:
        st.markdown(f"<div class='alarm-low'>⚠️ МАЛО ФН: Всего {int(fn_total)} шт на выбранных точках!</div>", unsafe_allow_html=True)

    # Таблица и График
    st.metric("ОБЩИЙ ЗАПАС ФН (ШТ)", f"{int(fn_total)}")
    st.dataframe(df_f, use_container_width=True)
    
    if kkt > 0:
        fig = px.pie(df_f, values=df_f.columns[5], names=c_col, hole=0.5, title="Доли ККТ")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>🚚 ЛОГИСТИКА: ПОЛНЫЙ МАССИВ</h1>", unsafe_allow_html=True)
    
    # ФИЛЬТРЫ ЛОГИСТИКИ (Партнер, Получатель, Номер)
    st.sidebar.subheader("🔍 Глубокая фильтрация")
    search = st.sidebar.text_input("🔍 Поиск по номеру/тексту:")
    
    # B - Партнер (1), K - Номер (10), L - Деньги (11)
    # Предположим, Получатель в столбце C(2) или D(3)
    sel_lp = st.sidebar.multiselect("Отправитель (Партнер):", sorted(df_l.iloc[:, 1].unique().astype(str)))
    sel_rec = st.sidebar.multiselect("Получатель/Город:", sorted(df_l.iloc[:, 2].unique().astype(str)))
    df_res = df_l.copy()
    if sel_lp: df_res = df_res[df_res.iloc[:, 1].astype(str).isin(sel_lp)]
    if sel_rec: df_res = df_res[df_res.iloc[:, 2].astype(str).isin(sel_rec)]
    if search:
        df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

    # Расчет денег (Столбец L)
    money = df_res.iloc[:, 11].apply(clean_num).sum()
    st.metric("СУММА ОБЯЗАТЕЛЬСТВ", f"{money:,.0f} ₽".replace(',', ' '))

    st.write("### 📋 Полная информация по логистике")
    st.dataframe(df_res, use_container_width=True)

    if money > 0:
        fig_l = px.pie(df_res, values=df_res.iloc[:, 11].apply(clean_num), names=df_res.columns[1], 
                       hole=0.5, title="Распределение денег по партнерам")
        st.plotly_chart(fig_l, use_container_width=True)
