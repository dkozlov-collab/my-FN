import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL CONTROL 2026")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 24px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 10px; background-color: #F8F9FA; }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА АККАУНТОВ (Изоляция партнеров) ---
# Каждый видит только строки, содержащие его "ID" во 2-м столбце (Партнер)
USER_DB = {
    "admin": {"pass": "admin777", "role": "ALL"},
    "ab1": {"pass": "ab2026", "role": "АБ"},
    "atml": {"pass": "atmgo", "role": "ATM"},
    "br": {"pass": "br123", "role": "БР"}
}

# --- 3. АВТОРИЗАЦИЯ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 RBS СИСТЕМА УПРАВЛЕНИЯ</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u = st.text_input("Логин").lower().strip()
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            if u in USER_DB and USER_DB[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u]["role"]
                st.rerun()
            else: st.error("❌ Доступ запрещен")
    st.stop()

# --- 4. ЗАГРУЗКА ДАННЫХ (СКЛАД И ЛОГИСТИКА) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_all()

# --- 5. ЖЕСТКАЯ ФИЛЬТРАЦИЯ (ИЗОЛЯЦИЯ) ---
role = st.session_state.user_role

if role == "ALL":
    st.sidebar.success("РЕЖИМ: АДМИНИСТРАТОР")
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Сортировка по партнерам:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    # ПАРТНЕР ВИДИТ ТОЛЬКО СВОЁ (и на складе, и в отправках)
    st.sidebar.info(f"Аккаунт: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 6. ОСНОВНОЙ ФУНКЦИОНАЛ ---
st.markdown(f"### Панель управления: {role}")
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА", "📦 СКЛАД (80 СТ)", "🚚 ОТПРАВКИ (ЛОГИСТИКА)"])

with t1:
    st.write("#### 📊 Сводные итоги")
    # Список столбцов для аналитики (План, Мин, ККТ, ФН, SIM, В пути, Расход)
    cols_map = {
        df_s.columns[1]: "ПАРТНЕР",
        df_s.columns[3]: "План",
        df_s.columns[4]: "Мин. ост",
        df_s.columns[5]: "ККТ",
        df_s.columns[6]: "ФН-15",
        df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM",
        df_s.columns[9]: "В пути",
        df_s.columns[10]: "Расход ФН-15 (мес)",
        df_s.columns[11]: "Расход ФН-36 (мес)"
    }
    
    df_calc = df_s.copy()
    for c in list(cols_map.keys())[1:]: df_calc[c] = df_calc[c].apply(to_n)
        # Убираем "нулевую" строку
    df_calc = df_calc[~df_calc.iloc[:, 1].astype(str).isin(["0", "0.0", ""])]
    
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # ИТОГО
    total = summary.sum(numeric_only=True).to_frame().T
    total["ПАРТНЕР"] = "ОБЩИЙ ИТОГ"
    summary = pd.concat([summary, total], ignore_index=True)
    
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("#### 📦 Склад (Сортировка активна)")
    # Поиск по складу для удобства
    search_s = st.text_input("🔍 Поиск по складу:", key="s_search")
    if search_s:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("#### 🚚 Ваши отправки и логистика")
    search_l = st.text_input("🔍 Найти ТТН или город:", key="l_search")
    if search_l:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
