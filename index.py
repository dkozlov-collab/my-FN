import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL ERP")

# --- 2. БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u = st.text_input("Логин").lower().strip()
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            if u in USER_DB and USER_DB[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u]["partner"]
                st.rerun()
            else: st.error("Ошибка входа")
    st.stop()

# --- 3. ЗАГРУЗКА ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load():
    try:
        # Берем 80 столбцов склада
        df = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        # Удаляем пустые строки с партнером "0"
        df = df[~df.iloc[:, 1].astype(str).isin(["0", "0.0", ""])]
        return df
    except: return pd.DataFrame()

df_raw = load()

# --- 4. ФИЛЬТРАЦИЯ ПАРТНЕРОВ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.header("Сортировка партнеров")
    all_partners = sorted(df_raw.iloc[:, 1].unique().astype(str))
    sel_p = st.sidebar.multiselect("Выберите партнеров:", all_partners)
    df = df_raw[df_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_raw
else:
    df = df_raw[df_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 5. КОНТЕНТ ---
st.markdown(f"## RBS GLOBAL: {role}")
t1, t2 = st.tabs(["🔢 АНАЛИТИКА (СВОДНЫЕ ИТОГИ)", "📦 СКЛАД (СОРТИРОВКА)"])

with t1:
    st.write("### 📊 Сводные итоги по всем столбцам")
    
    # Карта столбцов (укажи номера столбцов из Excel, если они сдвинуты)
    # Сейчас берем: 1-Партнер, 3-План, 4-Мин, 5-ККТ, 6-ФН15, 7-ФН36, 8-SIM, 9-В пути, 10-Расход15, 11-Расход36
    cols_to_sum = {
        df.columns[1]: "ПАРТНЕР",
        df.columns[3]: "План",
        df.columns[4]: "Мин.ост",
        df.columns[5]: "ККТ",
        df.columns[6]: "ФН 15",
        df.columns[7]: "ФН 36",
        df.columns[8]: "SIM",
        df.columns[9]: "В пути",
        df.columns[10]: "Расход 15 (мес)",
        df.columns[11]: "Расход 36 (мес)"
    }
    
    df_calc = df.copy()
    # Превращаем всё в числа для суммы
    for c in list(cols_to_sum.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
    
    # Группируем и считаем итоги
    summary = df_calc.groupby(df.columns[1])[list(cols_to_sum.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_to_sum, inplace=True)
    
    # Добавляем строку ИТОГО в самый низ
    total_row = summary.sum(numeric_only=True).to_frame().T
    total_row["ПАРТНЕР"] = "ОБЩИЙ ИТОГ"
    summary = pd.concat([summary, total_row], ignore_index=True)
    
    # Вывод таблицы итогов (без лишних фильтров, просто цифры)
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 📦 Склад (Сортировка по всем 80 столбцам)")
    # Здесь можно нажать на любой заголовок и отсортировать
    st.data_editor(df, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
