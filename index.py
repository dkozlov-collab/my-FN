import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(layout="wide", page_title="RBS TOTAL CONTROL")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 26px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 10px; background-color: #F8F9FA; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"}
}

# --- 3. СИСТЕМА ВХОДА ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В RBS GLOBAL</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u = st.text_input("Логин (admin)")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            u_check = u.lower().strip()
            if u_check in USER_DB and USER_DB[u_check]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u_check]["partner"]
                st.rerun()
            else:
                st.error("❌ Неверный логин или пароль")
    st.stop()

# --- 4. ЗАГРУЗКА ДАННЫХ (5000 СТРОК) ---
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
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load()

# --- 5. ФУНКЦИЯ ФИЛЬТРАЦИИ ПО СТОЛБЦАМ ---
def apply_table_filters(df, key_id):
    st.write("### 🔍 Фильтры по столбцам")
    # Берем важные столбцы для фильтрации (Партнер, Город, Статус и т.д.)
    filter_names = df.columns[1:7] 
    ui_cols = st.columns(len(filter_names))
    df_res = df.copy()
    
    for i, col in enumerate(filter_names):
        opts = sorted([str(x) for x in df[col].unique() if str(x) not in ["0", "0.0", ""]])
        with ui_cols[i]:
            sel = st.selectbox(f"{col}", ["Все"] + opts, key=f"{key_id}_{col}")
            if sel != "Все":
                df_res = df_res[df_res[col].astype(str) == sel]
    return df_res

# --- 6. ЛОГИКА ФИЛЬТРАЦИИ ПО РОЛИ ---
role = st.session_state.user_role
df_s = df_s_raw.copy()
df_l = df_l_raw.copy()

if role != "ALL":
    df_s = df_s[df_s.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l[df_l.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 7. КОНТЕНТ ---
st.markdown(f"<div class='main-header'>RBS GLOBAL CONTROL: {role}</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА ЦИФРЫ", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА (5000)"])

with t1:
    st.write("### 📊 Сводные итоги")
    cols_map = {
        df_s.columns[1]: "ПАРТНЕР", df_s.columns[3]: "План", df_s.columns[4]: "Мин.ост",
        df_s.columns[5]: "ККТ", df_s.columns[6]: "ФН-15", df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM", df_s.columns[9]: "В пути"
    }
    df_calc = df_s.copy()
    for c in list(cols_map.keys())[1:]: df_calc[c] = df_calc[c].apply(to_n)
    
    # Удаляем пустые/нулевые строки (строка "0" больше не вылезет)
    df_calc = df_calc[~df_calc.iloc[:, 1].astype(str).isin(["0", "0.0", ""])]
    
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # Итоговая строка
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["ПАРТНЕР"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    # Метрики
    m1, m2, m3 = st.columns(3)
    m1.metric("ККТ ИТОГО", f"{int(itogo['ККТ'].iloc[0])} шт")
    m2.metric("ФН ИТОГО", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    log_sum = df_l.iloc[:, 11].apply(to_n).sum()
    m3.metric("ЛОГИСТИКА (₽)", f"{int(log_sum):,} ₽".replace(",", " "))
    
    st.divider()
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    # Применяем фильтрацию по столбцам к складу
    df_s_final = apply_table_filters(df_s, "sklad")
    st.data_editor(df_s_final, use_container_width=True, height=600, hide_index=True)

with t3:
    # Применяем фильтрацию по столбцам к логистике
    df_l_final = apply_table_filters(df_l, "logist")
    st.data_editor(df_l_final, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
