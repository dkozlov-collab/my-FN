import streamlit as st
import pandas as pd
import plotly.express as px

# Масштабная настройка под Pocophone (Белый дизайн)
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 34px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКА (Дима, проверь, чтобы доступ в таблице был открыт!)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.').replace('\xa0', '')
        return int(float(s))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        col_clean = str(col).lower().replace('\n', ' ').strip()
        if any(word.lower() in col_clean for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        # ЗАДАЧА: А:R до 80 строки
        df = pd.read_csv(URL).iloc[:80, :18].fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

st.markdown("<h1>🏛️ RBS: ЦЕНТР УПРАВЛЕНИЯ СТРУКТУРОЙ</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # 1. ПОИСК КОЛОНОК (Решает KeyError)
    c_sp    = find_col(df_raw, ['партнер', 'сервис'])
    c_city  = find_col(df_raw, ['склад', 'город'])
    c_kkt   = find_col(df_raw, ['ккт', 'наличие'])
    c_spent = find_col(df_raw, ['расход', 'истратил'])
    c_money = find_col(df_raw, ['сумма', 'стоимость', '15-фн'])
    c_exit  = find_col(df_raw, ['выезд', 'тип рег'])

    # Чистим цифры (защита от TypeError)
    for col in [c_kkt, c_spent, c_money]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # 2. ФИЛЬТРЫ (Защита от TypeError в сортировке)
    st.write("### 🔍 Глобальная фильтрация")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        sp_list = sorted([str(x) for x in df_raw[c_sp].unique() if str(x) not in ['0', '']]) if c_sp else []
        sel_sp = st.multiselect("Сервис-Партнер", sp_list)
    with f2:
        city_list = sorted([str(x) for x in df_raw[c_city].unique() if str(x) not in ['0', '']]) if c_city else []
        sel_city = st.multiselect("Город / Склад", city_list)
    with f3:
        exit_list = sorted([str(x) for x in df_raw[c_exit].unique() if str(x) not in ['0', '']]) if c_exit else []
        sel_exit = st.multiselect("Тип выезда", exit_list)

    # Применяем фильтры
    df = df_raw.copy()
    if sel_sp: df = df[df[c_sp].astype(str).isin(sel_sp)]
    if sel_city: df = df[df[c_city].astype(str).isin(sel_city)]
    if sel_exit: df = df[df[c_exit].astype(str).isin(sel_exit)]

    # 3. ИТОГИ (МЕТРИКИ)
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("РАСХОД ФН (ИТОГО)", f"{df[c_spent].sum() if c_spent else 0} шт")
    m2.metric("ДЕНЕЖНЫЙ МАССИВ", f"{df[c_money].sum() if c_money else 0:,.0f} ₽".replace(',', ' '))
    m3.metric("ОСТАТОК ККТ", f"{df[c_kkt].sum() if c_kkt else 0} шт")

    # 4. ГРАФИКИ-БУБЛИКИ
    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        if c_spent and df[df[c_spent]>0].any().any():
            fig_fn = px.pie(df[df[c_spent]>0], values=c_spent, names=c_city if c_city else c_sp, 
                            hole=0.5, title="🔵 Доли расходов ФН")
            st.plotly_chart(fig_fn, use_container_width=True)
    with g2:
        if c_kkt and df[df[c_kkt]>0].any().any():
            fig_kkt = px.pie(df[df[c_kkt]>0], values=c_kkt, names=c_city if c_city else c_sp, 
                             hole=0.5, title="🟢 Доли остатков ККТ")
            st.plotly_chart(fig_kkt, use_container_width=True)

    # 5. ТАБЛИЦА МАССИВА
    st.write("### 📋 Полный реестр (A:R)")
    st.dataframe(df, use_container_width=True, hide_index=True)
    else:
    st.error("Система не видит данные. Дима, проверь доступ 'Все, у кого есть ссылка' в таблице!")
