import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКА ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide", page_title="RBS PROFESSIONAL DATABASE")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-header { font-size: 28px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
    /* Стиль для больших таблиц */
    [data-testid="stMetricValue"] { color: #007BFF !important; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. МОЩНЫЙ ЗАГРУЗЧИК (ДО 5000 СТРОК) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=10)
def load_big_data():
    try:
        # Читаем склад (80 столбцов)
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna("")
        # Читаем логистику (до 5000 строк)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna("")
        return s, l
    except Exception as e:
        st.error(f"Ошибка загрузки данных. Проверь доступ в Google: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_big_data()

# --- 3. ГЛОБАЛЬНЫЙ ДВИЖОК САЙТА ---
st.markdown("<div class='main-header'>RBS: СКЛАД И ЛОГИСТИКА (УПРАВЛЕНИЕ)</div>", unsafe_allow_html=True)

# Сайдбар для быстрой навигации
st.sidebar.header("Фильтрация")
global_search = st.sidebar.text_input("🔍 Поиск по всей базе:")

# Вкладки
tab_s, tab_l = st.tabs(["📦 СКЛАД (80 СТОЛБЦОВ)", "🚚 ЛОГИСТИКА (ДО 5000 СТРОК)"])

def apply_global_filter(df, query):
    if query:
        mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        return df[mask]
    return df

with tab_s:
    st.write("### Остатки на складах")
    filtered_s = apply_global_filter(df_s, global_search)
    
    # Использование data_editor дает встроенную фильтрацию по столбцам
    st.data_editor(
        filtered_s,
        use_container_width=True,
        height=700,
        hide_index=True,
        column_config={col: st.column_config.Column(width="medium") for col in filtered_s.columns}
    )
    st.caption(f"Отображено строк: {len(filtered_s)}")

with tab_l:
    st.write("### Логистические потоки")
    filtered_l = apply_global_filter(df_l, global_search)
    
    # Настройка для удобного чтения больших данных
    st.data_editor(
        filtered_l,
        use_container_width=True,
        height=700,
        hide_index=True,
        column_config={col: st.column_config.Column(width="medium") for col in filtered_l.columns}
    )
    st.caption(f"Всего записей в логистике: {len(filtered_l)}")

# --- 4. ФУНКЦИЯ ОЧИСТКИ (ДЛЯ РАСЧЕТОВ) ---
def to_n(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0
