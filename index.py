import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под Pocophone
st.set_page_config(page_title="RBS: Склад и Финансы", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .total-box { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 2px solid #007BFF; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        return int(float(str(val).replace(' ', '').replace('₽', '').replace(',', '.').replace('\xa0', '')))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        if any(word.lower() in str(col).lower().strip() for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        # Диапазон A:Q (0:17) и 80 строк
        df = pd.read_csv(URL).iloc[:80, 0:17].fillna(0)
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Ищем колонки
    c_city = find_col(df_raw, ['склад', 'город'])
    c_sp = find_col(df_raw, ['партнер', 'сервис'])
    c_kkt = find_col(df_raw, ['ккт', 'наличие'])
    c_fn15 = find_col(df_raw, ['фн-15', 'фн 15'])
    c_fn36 = find_col(df_raw, ['фн-36', 'фн 36'])
    c_money = find_col(df_raw, ['сумма', 'деньги', 'стоимость'])

    # Чистим цифры
    for c in [c_kkt, c_fn15, c_fn36, c_money]:
        if c: df_raw[c] = df_raw[c].apply(clean_num)

    # --- ПУЛЬТ ФИЛЬТРАЦИИ ---
    st.sidebar.title("🔍 ФИЛЬТРЫ АНАЛИЗА")
    
    # Фильтр по Партнерам
    partners = ["Все"] + sorted([str(x) for x in df_raw[c_sp].unique() if str(x) != '0']) if c_sp else ["Все"]
    sel_p = st.sidebar.multiselect("Выберите Партнеров (АБ и др.):", partners, default="Все")
    
    # Фильтр по Городам
    cities = ["Все"] + sorted([str(x) for x in df_raw[c_city].unique() if str(x) != '0']) if c_city else ["Все"]
    sel_c = st.sidebar.multiselect("Выберите Города:", cities, default="Все")

    # Применяем фильтрацию к данным
    df = df_raw.copy()
    if "Все" not in sel_p and sel_p:
        df = df[df[c_sp].astype(str).isin(sel_p)]
    if "Все" not in sel_c and sel_c:
        df = df[df[c_city].astype(str).isin(sel_c)]

    # --- САЙТ ---
    st.markdown("<h1>🏛️ RBS: УМНЫЙ МОНИТОРИНГ</h1>", unsafe_allow_html=True)
    
    # Итоги по фильтру
    st.markdown("<div class='total-box'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("ВЫБРАННЫЙ ОБОРОТ", f"{df[c_money].sum() if c_money else 0:,.0f} ₽".replace(',', ' '))
    col2.metric("ККТ В НАЛИЧИИ", f"{df[c_kkt].sum() if c_kkt else 0} шт")
    col3.metric("ЗАПАС ФН (15/36)", f"{(df[c_fn15].sum() if c_fn15 else 0) + (df[c_fn36].sum() if c_fn36 else 0)} шт")
    st.markdown("</div>", unsafe_allow_html=True)

    # График (Бублик) по выбранному
    if c_money and df[c_money].sum() > 0:
        fig = px.pie(df[df[c_money]>0], values=c_money, names=c_city, hole=0.5, 
                     title="📊 Доли оборота (по фильтру)")
        st.plotly_chart(fig, use_container_width=True)

    # Таблица результата
    st.write("### 📋 Результаты анализа (A:Q)")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.error("Данные не найдены!")
