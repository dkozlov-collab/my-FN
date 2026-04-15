import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКА БЕЗОПАСНОСТИ И ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide", page_title="RBS SECURE ACCESS")

# Стили (Светлая тема)
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 32px !important; font-weight: 800; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ПОЛЬЗОВАТЕЛЕЙ (РУЧНАЯ НАСТРОЙКА) ---
# Логин : {пароль, фильтр_имени_партнера}
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "AB"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "bank": {"pass": "bank99", "partner": "BANK"}
}

# --- ФУНКЦИЯ ВХОДА ---
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В СИСТЕМУ RBS</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            user = st.text_input("Логин")
            pw = st.text_input("Пароль", type="password")
            if st.button("Войти"):
                if user in USER_DB and USER_DB[user]["pass"] == pw:
                    st.session_state.auth = True
                    st.session_state.user_role = USER_DB[user]["partner"]
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
        st.stop()

login()

# --- 2. ЗАГРУЗКА ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_data():
    try:
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_data()

# --- 3. АВТО-ФИЛЬТРАЦИЯ ПО РОЛИ ---
role = st.session_state.user_role

if role == "ALL":
    # Админ видит всё + может фильтровать вручную
    st.sidebar.success("Вы зашли как АДМИНИСТРАТОР")
    p_list = sorted(list(set(df_s_raw.iloc[:, 1].astype(str))))
    sel_p = st.sidebar.multiselect("Фильтр партнеров:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_l_raw
else:
    # Обычный партнер видит ТОЛЬКО свои данные (фильтр по части имени)
    st.sidebar.info(f"Доступ: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 4. ВКЛАДКИ ---
st.markdown(f"<div class='main-header'>ПАНЕЛЬ УПРАВЛЕНИЯ: {role}</div>", unsafe_allow_html=True)
tab_a, tab_s, tab_l = st.tabs(["🔢 АНАЛИТИКА ЦИФРЫ", "📦 СКЛАД ОСТАТКИ", "🚚 ЛОГИСТИКА"])

with tab_a:
    st.write("### 📈 ИТОГИ ПО СТОЛБЦАМ")
    c1, c2, c3 = st.columns(3)
    kkt = df_s.iloc[:, 5].apply(to_n).sum()
    fn = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    money = df_l.iloc[:, 11].apply(to_n).sum()
    
    c1.metric("ККТ", f"{int(kkt)} шт")
    c2.metric("ФН", f"{int(fn)} шт")
    c3.metric("ЛОГИСТИКА", f"{int(money):,} ₽".replace(",", " "))

    st.divider()
    # Сводная таблица по всем 80 столбцам
    cols_to_sum = df_s.columns[5:80]
    df_num = df_s.copy()
    for col in cols_to_sum: df_num[col] = df_num[col].apply(to_n)
    summary = df_num.groupby(df_s.columns[1])[cols_to_sum].sum().reset_index()
    st.write("#### Детальные остатки по позициям:")
    st.data_editor(summary, use_container_width=True, hide_index=True)
    with tab_s:
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with tab_l:
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("Выйти"):
    st.session_state.auth = False
    st.rerun()
    
