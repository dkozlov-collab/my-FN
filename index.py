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
