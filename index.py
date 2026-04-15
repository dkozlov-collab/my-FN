import streamlit as st
import pandas as pd

# Настройка под мобильный (Pocophone)
st.set_page_config(page_title="RBS: Прямой Массив", layout="wide")

# Чистый белый дизайн, чтобы всё было видно
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    h1 { color: #1A237E !important; font-family: sans-serif; text-align: center; border-bottom: 2px solid #007BFF; }
    .stDataFrame { border: 1px solid #DEE2E6; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=5)
def load_raw_data():
    try:
        # Читаем таблицу "как есть" без ограничений по именам
        df = pd.read_csv(URL).fillna("")
        # Берем первые 100 строк и столбцы A-R (0-18)
        df = df.iloc[:100, :19]
        return df
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return pd.DataFrame()

st.markdown("<h1>📊 ПОЛНЫЙ МАССИВ ДАННЫХ RBS</h1>", unsafe_allow_html=True)

df = load_raw_data()

if not df.empty:
    # --- ГЛАВНЫЙ ПОИСК ---
    # Позволяет искать по серийнику, городу или любому слову во всей таблице сразу
    search_query = st.text_input("🔍 Мгновенный поиск по всему массиву (введи серийник, город или партнера):")

    if search_query:
        # Фильтруем таблицу по любому совпадению
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # --- СТАТИСТИКА (Автоматическая) ---
    st.write("### 📌 Сводка по выбранным данным")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ВСЕГО СТРОК В ВЫБОРКЕ", len(df))
    
    # --- ТАБЛИЦА (ВСЕ ДАННЫЕ СРАЗУ) ---
    st.write("### 📋 Таблица остатков и расходов (A:R)")
    
    # Выводим таблицу, в которой можно нажать на любой заголовок для сортировки
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("💡 Совет: Нажми на название любого столбца в таблице выше, чтобы отсортировать данные (например, по расходу или остатку).")

else:
    st.warning("Таблица пустая или нет доступа. Проверь ссылку!")

import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под мобильный (Белый дизайн Pocophone)
st.set_page_config(page_title="RBS: Глобальное Управление", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 30px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; }
    /* Стиль кнопок фильтров */
    div.stSelectbox > label { font-weight: bold; color: #1A237E; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "": return 0
        return int(float(str(val).replace(' ', '').replace('₽', '').replace(',', '.')))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        if any(word.lower() in str(col).lower() for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL).head(100).fillna(0)
        return df
    except: return pd.DataFrame()

st.markdown("<h1>🏛️ RBS: МАССИВ И ФИЛЬТРЫ</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # 1. СТРУКТУРА КОЛОНОК (A:R)
    c_exit = find_col(df_raw, ['Тип рег', 'Выезд'])
    c_sp = find_col(df_raw, ['Партнер'])
    c_city = find_col(df_raw, ['Склад', 'Город'])
    c_fn_spent = find_col(df_raw, ['истратил', 'Расход'])
    c_money = find_col(df_raw, ['сумма', '15-ФН'])

    # 2. РЯД КНОПОК-ФИЛЬТРОВ (Продолжаем ряд)
    st.write("### 🛠️ Пульт управления данными")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        e_list = ["Все"] + sorted([str(x) for x in df_raw[c_exit].unique() if str(x) != '0']) if c_exit else ["Все"]
        sel_e = st.selectbox("1. ВЫЕЗДЫ", e_list)
    with col_f2:
        p_list = ["Все"] + sorted([str(x) for x in df_raw[c_sp].unique() if str(x) != '0']) if c_sp else ["Все"]
        sel_p = st.selectbox("2. ПАРТНЕРЫ", p_list)
    with col_f3:
        c_list = ["Все"] + sorted([str(x) for x in df_raw[c_city].unique() if str(x) != '0']) if c_city else ["Все"]
        sel_c = st.selectbox("3. ГОРОДА", c_list)
    with col_f4:
        # Фильтр по наличию расхода
        sel_spent = st.selectbox("4. РАСХОД", ["Все", "Только с расходом", "Без расхода"])

    # ПРИМЕНЕНИЕ ФИЛЬТРОВ
    df = df_raw.copy()
    if sel_e != "Все": df = df[df[c_exit].astype(str) == sel_e]
    if sel_p != "Все": df =
