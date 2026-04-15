import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL ERP 2026")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 15px; background-color: #F8F9FA; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ДОСТУПЫ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "br": {"pass": "br123", "partner": "БР"}
}

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
            else: st.error("Неверный логин или пароль")
    st.stop()

# --- 3. ЗАГРУЗКА (5000 СТРОК) ---
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
        # Склад до 1000, Логистика до 5000
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load()

# --- 4. СКВОЗНАЯ ФИЛЬТРАЦИЯ ---
st.sidebar.header("⚙️ ГЛОБАЛЬНЫЕ ФИЛЬТРЫ")

role = st.session_state.user_role

# Если админ - показываем все фильтры
if role == "ALL":
    # 1. Фильтр по Партнерам
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Бизнес-партнеры:", p_list)
    
    # 2. Фильтр по Городам/Отправителям (берем из 2 и 3 столбцов)
    c_list = sorted(list(set(df_s_raw.iloc[:, 2].astype(str)) | set(df_l_raw.iloc[:, 3].astype(str))))
    sel_c = st.sidebar.multiselect("Города / Отправители:", [x for x in c_list if x not in ["0", "0.0", ""]])

    df_s = df_s_raw.copy()
    df_l = df_l_raw.copy()
    
    if sel_p:
        df_s = df_s[df_s.iloc[:, 1].isin(sel_p)]
        df_l = df_l[df_l.iloc[:, 1].isin(sel_p)]
    if sel_c:
        df_s = df_s[df_s.iloc[:, 2].astype(str).isin(sel_c)]
        df_l = df_l[df_l.iloc[:, 3].astype(str).isin(sel_c)]
else:
    # Если партнер - фильтруем только под него
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 5. КОНТЕНТ ---
st.markdown(f"<div class='main-header'>RBS GLOBAL: {role}</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА ЦИФРЫ", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА (5000)"])

with t1:
    st.write("### 📊 Сводные данные")
    
    # Расчеты (как в be81a3e0)
    cols_map = {
        df_s.columns[1]: "ПАРТНЕР",
        df_s.columns[3]: "План",
    df_s.columns[4]: "Мин.ост",
        df_s.columns[5]: "ККТ",
        df_s.columns[6]: "ФН-15",
        df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM",
        df_s.columns[9]: "В пути"
    }
    
    df_calc = df_s.copy()
    for c in list(cols_map.keys())[1:]: df_calc[c] = df_calc[c].apply(to_n)
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # ИТОГО
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["ПАРТНЕР"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("ККТ ВСЕГО", f"{int(itogo['ККТ'].iloc[0])} шт")
    m2.metric("ФН ВСЕГО", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    m3.metric("ЛОГИСТИКА", f"{int(df_l.iloc[:, 11].apply(to_n).sum()):,} ₽".replace(",", " "))
    
    st.divider()
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 📦 Полный склад")
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Логистика (все посылки)")
    l_search = st.text_input("🔍 Быстрый поиск по логистике (ТТН, Серийник, Город):")
    df_l_disp = df_l.copy()
    if l_search:
        df_l_disp = df_l_disp[df_l_disp.apply(lambda r: r.astype(str).str.contains(l_search, case=False).any(), axis=1)]
    st.data_editor(df_l_disp, use_container_width=True, height=700, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
