import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ И СТИЛЬ ---
st.set_page_config(layout="wide", page_title="RBS TOTAL CONTROL 2026")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 24px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 10px; background-color: #F8F9FA; }
    .main-header { font-size: 26px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
    .summary-table { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "br": {"pass": "br123", "partner": "БР"}
}

# --- 3. АВТОРИЗАЦИЯ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В RBS СИСТЕМУ</h1>", unsafe_allow_html=True)
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

# --- 4. ЗАГРУЗКА ДАННЫХ ---
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

# --- 5. ФИЛЬТР ПО РОЛИ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.success("ДОСТУП: АДМИНИСТРАТОР")
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Фильтр партнеров:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    st.sidebar.info(f"ПАРТНЕР: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 6. КОНТЕНТ ---
st.markdown(f"<div class='main-header'>ОТЧЕТ RBS: {role}</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА (ОСТАТКИ)", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА"])

with t1:
    st.write("### 📊 Сводные цифры по партнерам (как в таблице)")
    
    # Расчет по столбцам из твоего фото (be81a3e0)
    # Предполагаем индексы столбцов на основе твоих данных:
    # 3: План, 4: Мин.остаток, 5: ККТ, 6: ФН-15, 7: ФН-36, 8: SIM, 9: В пути
    
    cols = {
        df_s.columns[1]: "СП",
        df_s.columns[3]: "План",
        df_s.columns[4]: "Мин. остаток",
        df_s.columns[5]: "Остатки ККТ",
        df_s.columns[6]: "Остатки ФН-15",
        df_s.columns[7]: "Остатки ФН-36",
        df_s.columns[8]: "Остатки SIM",
        df_s.columns[9]: "В пути ККТ"
    }
    
    df_calc = df_s.copy()
    for c in list(cols.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
        
    summary = df_calc.groupby(df_s.columns[1])[list(cols.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols, inplace=True)
    
    # Добавляем строку ИТОГО
    totals = summary.sum(numeric_only=True).to_frame().T
    totals["СП"] = "ИТОГО"
    summary = pd.concat([summary, totals], ignore_index=True)
    
    # Вывод карточек сверху
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ККТ ИТОГО", f"{int(totals['Остатки ККТ'].iloc[0])}")
    m2.metric("ФН ИТОГО", f"{int(totals['Остатки ФН-15'].iloc[0] + totals['Остатки ФН-36'].iloc[0])}")
    m3.metric("SIM ИТОГО", f"{int(totals['Остатки SIM'].iloc[0])}")
    m4.metric("В ПУТИ", f"{int(totals['В пути ККТ'].iloc[0])}")

    st.divider()
    st.write("#### Детальная таблица остатков:")
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with t3:
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()
    
