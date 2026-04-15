import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ И СТИЛЬ ---
st.set_page_config(layout="wide", page_title="RBS SMART SYSTEM")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 15px; background-color: #F8F9FA; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "AB"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "bank": {"pass": "bank99", "partner": "BANK"}
}

# --- АВТОРИЗАЦИЯ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В RBS SYSTEM</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
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

# --- ЗАГРУЗКА ДАННЫХ ---
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

# --- ФИЛЬТР ПО РОЛИ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.success("ДОСТУП: АДМИНИСТРАТОР")
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if x not in [0, "0", ""]])
    sel_p = st.sidebar.multiselect("Фильтр партнеров:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    st.sidebar.info(f"ДОСТУП: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- ОТОБРАЖЕНИЕ ---
st.markdown(f"<div class='main-header'>ОТЧЕТ: {role}</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА (ИТОГИ ПО СТОЛБЦАМ)", "📦 ВЕСЬ СКЛАД", "🚚 ЛОГИСТИКА"])

with t1:
    st.write("### 📊 Сводные цифры по всем позициям")
    
    # Считаем суммы для аналитики
    cols_to_sum = df_s.columns[5:80]
    df_num = df_s.copy()
    for c in cols_to_sum:
        df_num[c] = df_num[c].apply(to_n)
    
    # Группировка: каждый партнер видит только свои итоги по столбцам
    summary = df_num.groupby(df_s.columns[1])[cols_to_sum].sum().reset_index()
    
    # Метрики сверху (ККТ, ФН, Логистика)
    kkt = df_s.iloc[:, 5].apply(to_n).sum()
    fn = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    money = df_l.iloc[:, 11].apply(to_n).sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("ККТ (ВСЕГО)", f"{int(kkt)} шт")
    m2.metric("ФН (ВСЕГО)", f"{int(fn)} шт")
    m3.metric("ЛОГИСТИКА", f"{int(money):,} ₽".replace(",", " "))
    
    st.divider()
    st.write("#### Детальная таблица остатков по всем 80 столбцам:")
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 📦 Полный реестр склада")
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Полный реестр логистики")
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
