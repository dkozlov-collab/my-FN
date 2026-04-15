import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под Pocophone (Чистый белый дизайн)
st.set_page_config(page_title="RBS: Главная Аналитика", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #212529; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1, h2, h3 { color: #343A40 !important; font-family: sans-serif; }
    .main-box { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background: #F0F8FF; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val): return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    for c in df.columns:
        if key.lower() in str(c).replace('\n', ' ').lower(): return c
    return None

@st.cache_data(ttl=10)
def load_data():
    try:
        # Берем диапазон A:R, строки до 80
        df = pd.read_csv(URL).fillna(0)
        df = df.iloc[:80, :18]
        return df
    except: return pd.DataFrame()

st.title("🚀 ГЛАВНАЯ АНАЛИТИКА RBS")

df_raw = load_data()

if not df_raw.empty:
    # Динамический поиск колонок
    c_exit = find_col(df_raw, 'Тип рег') # Выезды
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_kkt = find_col(df_raw, 'ККТ')
    c_fn_used = find_col(df_raw, 'истратил') # Истрачено ФН
    c_sum = find_col(df_raw, 'Сумма')

    # --- БЛОК ФИЛЬТРОВ (Сверху, компактно) ---
    with st.expander("🔍 Настройки фильтрации (Выезды, Партнеры, Города)"):
        f1, f2, f3 = st.columns(3)
        with f1:
            e_list = ["Все типы"] + sorted([str(x) for x in df_raw[c_exit].unique() if x != 0]) if c_exit else ["Все"]
            sel_e = st.selectbox("Тип выезда", e_list)
        with f2:
            p_list = ["Все партнеры"] + sorted([str(x) for x in df_raw[c_sp].unique() if x != 0]) if c_sp else ["Все"]
            sel_p = st.selectbox("Сервис-Партнер", p_list)
        with f3:
            c_list = ["Все города"] + sorted([str(x) for x in df_raw[c_city].unique() if x != 0]) if c_city else ["Все"]
            sel_c = st.selectbox("Город/Склад", c_list)

    # Применение фильтров
    df = df_raw.copy()
    if sel_e != "Все типы": df = df[df[c_exit].astype(str) == sel_e]
    if sel_p != "Все партнеры": df = df[df[c_sp].astype(str) == sel_p]
    if sel_c != "Все города": df = df[df[c_city].astype(str) == sel_c]

    # Подготовка цифр
    for col in [c_kkt, c_fn_used, c_sum]:
        if col: df[col] = df[col].apply(clean_num)

    # --- ГЛАВНЫЕ ПОКАЗАТЕЛИ ---
    st.markdown("### 💰 ТЕКУЩЕЕ СОСТОЯНИЕ")
    m1, m2, m3 = st.columns(3)
    
    total_money = df[c_sum].sum() if c_sum else 0
    total_kkt = df[c_kkt].sum() if c_kkt else 0
    total_fn_used = df[c_fn_used].sum() if c_fn_used else 0
    
    m1.metric("ДЕНЕГ В ТОВАРЕ", f"{total_money:,.0f} ₽".replace(',', ' '))
    m2.metric("ОСТАТОК ККТ", f"{total_kkt} шт")
    m3.metric("ИСТРАЧЕНО ФН", f"{total_fn_used} шт")

    st.divider()

    # --- ГРАФИК РАСХОДА ---
    st.markdown("### 📈 ГРАФИК РАСХОДА И ОСТАТКОВ")
    if c_city and (total_kkt > 0 or total_fn_used > 0):
        # Создаем данные для графика расхода
        chart_data = df[df[c_kkt] > 0].nlargest(10, c_kkt)
        fig = px.bar(chart_data, x=c_city, y=[c_kkt, c_fn_used] if c_fn_used else [c_kkt], 
                     barmode='group', title="Расход vs Остаток по городам")
        st.plotly_chart(fig, use_container_width=True)

    # --- ДЕТАЛЬНАЯ ТАБЛИЦА ---
    st.markdown("### 📋 РЕЕСТР")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.error("Ошибка загрузки! Проверь доступ к таблице.")
