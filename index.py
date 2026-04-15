import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка "Масштабного" интерфейса 2026
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

# Чистый белый дизайн под твой Pocophone
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 35px; font-weight: bold; }
    h1, h2, h3 { color: #1A237E !important; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

# Умная чистка чисел (защита от TypeError)
def clean_num(val):
    try:
        if pd.isna(val) or val == "": return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

# Умный поиск колонок (защита от KeyError)
def find_col(df, key):
    for c in df.columns:
        if key.lower() in str(c).replace('\n', ' ').lower(): return c
    return None

@st.cache_data(ttl=5)
def load_massive_data():
    try:
        df = pd.read_csv(URL).head(100).fillna(0)
        return df
    except: return pd.DataFrame()

st.title("🏛️ RBS: ГЛОБАЛЬНЫЙ МАССИВ И РАСХОДЫ")

df_raw = load_massive_data()

if not df_raw.empty:
    # 1. АВТОПОИСК КОЛОНОК (Решает KeyError)
    c_exit = find_col(df_raw, 'Тип рег') or find_col(df_raw, 'Выезд')
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_kkt = find_col(df_raw, 'ККТ')
    c_fn_spent = find_col(df_raw, 'истратил') or find_col(df_raw, 'Расход')
    c_sum = find_col(df_raw, 'Сумма')

    # Очищаем все числовые массивы
    for col in [c_kkt, c_fn_spent, c_sum]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # 2. ГЛАВНЫЕ ЦИФРЫ (ВЕСЬ МАССИВ)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("ОБЩИЙ РАСХОД ФН", f"{df_raw[c_fn_spent].sum() if c_fn_spent else 0} шт")
    with m2:
        st.metric("ДЕНЕЖНЫЙ МАССИВ", f"{df_raw[c_sum].sum() if c_sum else 0:,.0f} ₽".replace(',', ' '))
    with m3:
        st.metric("ОСТАТОК ККТ", f"{df_raw[c_kkt].sum() if c_kkt else 0} шт")

    st.divider()

    # 3. МАССИВНЫЕ ФИЛЬТРЫ (Защита от TypeError)
    st.subheader("🔍 Глобальная фильтрация структуры")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        # Превращаем всё в текст перед сортировкой (Защита от TypeError на фото 8)
        e_list = sorted([str(x) for x in df_raw[c_exit].unique() if str(x) != '0']) if c_exit else []
        sel_e = st.multiselect("Тип выезда", e_list)
    with f2:
        p_list = sorted([str(x) for x in df_raw[c_sp].unique() if str(x) != '0']) if c_sp else []
        sel_p = st.multiselect("Сервис-Партнер", p_list)
    with f3:
        c_list = sorted([str(x) for x in df_raw[c_city].unique() if str(x) != '0']) if c_city else []
        sel_city = st.multiselect("Город / Филиал", c_list)

    # Применение фильтров
    df_f = df_raw.copy()
    if sel_e: df_f = df_f[df_f[c_exit].astype(str).isin(sel_e)]
    if sel_p: df_f = df_f[df_f[c_sp].astype(str).isin(sel_p)]
    if sel_city: df_f = df_f[df_f[c_city].astype(str).isin(sel_city)]

    # 4. ГРАФИК РАСХОДА (МАССИВНЫЙ)
    st.subheader("📈 Расход ресурсов по филиалам")
    if c_city and c_fn_spent:
        fig_data = df_f[df_f[c_fn_spent] > 0].sort_values(c_fn_spent, ascending=False)
        if not fig_data.empty:
            fig = px.bar(fig_data, x=c_city, y=c_fn_spent, text_auto=True, 
                         color=c_fn_spent, color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

    # 5. ИТОГОВАЯ ТАБЛИЦА МАССИВА
    st.subheader("📋 Реестр всей структуры")
    st.dataframe(df_f, use_container_width=True, hide_index=True)

else:
    st.error("Система не видит таблицу. Дима, проверь кнопку 'Поделиться'!")
