import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под Pocophone (Чистый белый дизайн)
st.set_page_config(page_title="RBS: Глобальный Мониторинг", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; }
</style>
""", unsafe_allow_html=True)

# НОВАЯ ССЫЛКА (экспорт в CSV)
URL = "https://docs.google.com/spreadsheets/d/1m-HdbV_cEyJ5EW7OMyxkpuDgDgPajfnwgi7rvnm7hcE/export?format=csv"

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
        # Берем весь массив данных (A:R, первые 150 строк)
        df = pd.read_csv(URL).head(150).fillna(0)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа: {e}")
        return pd.DataFrame()

st.markdown("<h1>🏛️ RBS: ЦЕНТР УПРАВЛЕНИЯ (НОВАЯ БАЗА)</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Динамический поиск колонок (независимо от названий в новой таблице)
    c_exit = find_col(df_raw, ['выезд', 'тип рег', 'удаленно'])
    c_sp   = find_col(df_raw, ['партнер', 'сервис'])
    c_city = find_col(df_raw, ['склад', 'город', 'филиал'])
    c_spent = find_col(df_raw, ['истратил', 'расход', 'отправлено'])
    c_money = find_col(df_raw, ['сумма', 'денежн', 'стоимость'])
    c_kkt  = find_col(df_raw, ['ккт', 'остатки', 'наличие'])

    # Чистим цифры
    for col in [c_spent, c_money, c_kkt]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # --- ПУЛЬТ УПРАВЛЕНИЯ (Кнопки в ряд) ---
    st.write("### 🔍 Фильтрация массива")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        e_list = sorted([str(x) for x in df_raw[c_exit].unique() if str(x) not in ['0', '']]) if c_exit else []
        sel_e = st.multiselect("Тип выезда", e_list)
    with f2:
        p_list = sorted([str(x) for x in df_raw[c_sp].unique() if str(x) not in ['0', '']]) if c_sp else []
        sel_p = st.multiselect("Партнер", p_list)
    with f3:
        c_list = sorted([str(x) for x in df_raw[c_city].unique() if str(x) not in ['0', '']]) if c_city else []
        sel_city = st.multiselect("Город / Склад", c_list)

    # Применение фильтров
    df = df_raw.copy()
    if sel_e: df = df[df[c_exit].astype(str).isin(sel_e)]
    if sel_p: df = df[df[c_sp].astype(str).isin(sel_p)]
    if sel_city: df = df[df[c_city].astype(str).isin(sel_city)]

    # --- ГЛАВНАЯ ПАНЕЛЬ (ИТОГИ) ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("РАСХОД ФН (ИТОГО)", f"{df[c_spent].sum() if c_spent else 0} шт")
    m2.metric("ДЕНЕЖНЫЙ МАССИВ", f"{df[c_money].sum() if c_money else 0:,.0f} ₽".replace(',', ' '))
    m3.metric("ОСТАТОК ККТ", f"{df[c_kkt].sum() if c_kkt else 0} шт")

    # --- ГРАФИК РАСХОДА ---
    if c_city and c_spent and not df[df[c_spent]>0].empty:
        st.subheader("📈 Расход ресурсов по филиалам")
        fig = px.bar(df[df[c_spent]>0].sort_values(c_spent, ascending=False), 
                     x=c_city, y=c_spent, text_auto=True, color_discrete_sequence=['#007BFF'])
        st.plotly_chart(fig, use_container_width=True)

    # --- ПОЛНЫЙ МАССИВ (Таблица) ---
    st.subheader("📋 Детальный реестр (A:R)")
    st.dataframe(df.iloc[:, :18], use_container_width=True, hide_index=True)

else:
    st.error("Система не видит данные. Проверь доступ 'Все, у кого есть ссылка' в новой таблице!")
    
