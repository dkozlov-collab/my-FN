import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL ERP")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 15px; background-color: #F8F9FA; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. РУЧНАЯ БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "br": {"pass": "br123", "partner": "БР"}
}

# --- 3. СИСТЕМА ВХОДА ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В RBS SYSTEM</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            if u in USER_DB and USER_DB[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u]["partner"]
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
    st.stop()

# --- 4. ЗАГРУЗКА ДАННЫХ (CSV ИЗ GOOGLE) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load():
    try:
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        return s, l
    except:
        st.error("Ошибка доступа к Google Таблицам")
        return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load()

# --- 5. ФИЛЬТР ПО РОЛИ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.success("РЕЖИМ: АДМИНИСТРАТОР")
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Выберите партнера:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    st.sidebar.info(f"ДОСТУП: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 6. ОСНОВНОЙ КОНТЕНТ ---
st.markdown(f"<div class='main-header'>ОТЧЕТ: {role}</div>", unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["🔢 АНАЛИТИКА", "📦 СКЛАД", "🚚 ЛОГИСТИКА", "⚙️ СЕРВИС"])

with t1:
    st.write("### 📊 Сводные цифры остатков")
    
    # Ручной выбор столбцов для анализа (План, Мин.ост, ККТ, ФН, SIM, В пути)
    cols_map = {
        df_s.columns[1]: "ПАРТНЕР",
        df_s.columns[3]: "ПЛАН",
        df_s.columns[4]: "МИН.ОСТ",
        df_s.columns[5]: "ККТ",
        df_s.columns[6]: "ФН-15",
        df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM",
        df_s.columns[9]: "В ПУТИ"
    }
    
    df_calc = df_s.copy()
    for c in list(cols_map.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
        
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # Добавляем строку ИТОГО
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["ПАРТНЕР"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    # Крупные цифры
    c1, c2, c3 = st.columns(3)
    c1.metric("ККТ ВСЕГО", f"{int(itogo['ККТ'].iloc[0])} шт")
    c2.metric("ФН (15+36)", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    c3.metric("SIM-КАРТЫ", f"{int(itogo['SIM'].iloc[0])} шт")
    
    st.divider()
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 📦 Реестр склада (80 столбцов)")
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Логистика (5000 строк)")
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

with t4:
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()
    if st.button("Сбросить кэш данных"):
        st.cache_data.clear()
        st.rerun()
for c in list(cols_map.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
        
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # Считаем итоги для строки ИТОГО
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["ПАРТНЕР"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    # Карточки с главными цифрами
    m1, m2, m3 = st.columns(3)
    m1.metric("ККТ ВСЕГО", f"{int(itogo['ККТ'].iloc[0])} шт")
    m2.metric("ФН (ВСЕ МОДЕЛИ)", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    m3.metric("SIM-КАРТЫ", f"{int(itogo['SIM'].iloc[0])} шт")
    
    st.divider()
    # Таблица аналитики (можно сортировать по любому столбцу)
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 🔍 Склад с фильтрацией")
    # Глобальный поиск по всем 80 столбцам
    search_s = st.text_input("🔍 Быстрый поиск по складу (введите город, модель или серийник):")
    df_show_s = df_s.copy()
    if search_s:
        df_show_s = df_show_s[df_show_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    
    # Редактор позволяет сортировать и искать по столбцам
    st.data_editor(df_show_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Логистика (5000 строк)")
    search_l = st.text_input("🔍 Поиск по логистике (ТТН, Партнер):")
    df_show_l = df_l.copy()
    if search_l:
        df_show_l = df_show_l[df_show_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
    
    st.data_editor(df_show_l, use_container_width=True, height=600, hide_index=True)

with t4:
    st.write("### ⚙️ Управление")
    if st.button("Обновить данные из таблиц (Сбросить кэш)"):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        st.session_state.auth = False
        st.rerun()
