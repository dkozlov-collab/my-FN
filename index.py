import streamlit as st
import pandas as pd
import re

# --- 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ (LIGHT THEME) ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL ERP 2026")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #1C1C1E; }
    [data-testid="stMetricValue"] { color: #0047AB !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="metric-container"] { 
        background-color: #F2F2F7; border: 1px solid #D1D1D6; border-radius: 12px; padding: 15px;
    }
    .main-header { font-size: 26px; font-weight: 900; color: #000000; text-align: center; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #F2F2F7; padding: 5px; border-radius: 10px; }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА ПОЛЬЗОВАТЕЛЕЙ (ЛОГИНЫ) ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "br": {"pass": "br123", "partner": "БР"}
}

# --- 3. СИСТЕМА АВТОРИЗАЦИИ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 RBS SECURE SYSTEM</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u_in = st.text_input("Логин")
        p_in = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ В СИСТЕМУ", use_container_width=True):
            if u_in in USER_DB and USER_DB[u_in]["pass"] == p_in:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u_in]["partner"]
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
    st.stop()

# --- 4. ДВИЖОК ЗАГРУЗКИ ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        res = re.findall(r'\d+', str(v).replace(' ',''))
        return float(res[0]) if res else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load_all():
    try:
        s = pd.read_csv(S_URL).iloc[:1000, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        return s, l
    except Exception as e:
        st.error(f"Ошибка доступа к Google Таблицам: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_all()

# --- 5. СКВОЗНАЯ ФИЛЬТРАЦИЯ ПО РОЛИ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.success(f"Вы: АДМИНИСТРАТОР")
    p_opts = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Фильтр партнеров:", p_opts)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    st.sidebar.info(f"Доступ: {role}")
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 6. ОСНОВНОЙ КОНТЕНТ ---
st.markdown(f"<div class='main-header'>ОПЕРАЦИОННЫЙ ЦЕНТР: {role}</div>", unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["🔢 АНАЛИТИКА (ЦИФРЫ)", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА (5000 СТР)", "⚙️ СЕРВИС"])

with t1:
    st.write("### 📊 Сводные остатки по ключевым позициям")
    
    # Карта столбцов под твой Excel (be81a3e0)
    cols_map = {
        df_s.columns[1]: "СП",
        df_s.columns[3]: "План",
    df_s.columns[4]: "Мин. ост",
        df_s.columns[5]: "ККТ",
        df_s.columns[6]: "ФН-15",
        df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM",
        df_s.columns[9]: "В пути"
    }
    
    df_calc = df_s.copy()
    for c in list(cols_map.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
        
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # Строка ИТОГО
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["СП"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    # Метрики сверху
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ККТ (ИТОГО)", f"{int(itogo['ККТ'].iloc[0])} шт")
    c2.metric("ФН (ИТОГО)", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    c3.metric("SIM (ИТОГО)", f"{int(itogo['SIM'].iloc[0])} шт")
    c4.metric("В ПУТИ", f"{int(itogo['В пути'].iloc[0])} шт")

    st.divider()
    st.write("#### Сводная цифровая таблица:")
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.write("### 📦 Полный реестр склада (80 столбцов)")
    s_search = st.text_input("🔍 Фильтр склада (по любому слову):")
    df_s_disp = df_s.copy()
    if s_search:
        df_s_disp = df_s_disp[df_s_disp.apply(lambda r: r.astype(str).str.contains(s_search, case=False).any(), axis=1)]
    st.data_editor(df_s_disp, use_container_width=True, height=600, hide_index=True)

with t3:
    st.write("### 🚚 Логистика (До 5000 строк)")
    l_search = st.text_input("🔍 Фильтр логистики (ТТН, серийник):")
    df_l_disp = df_l.copy()
    if l_search:
        df_l_disp = df_l_disp[df_l_disp.apply(lambda r: r.astype(str).str.contains(l_search, case=False).any(), axis=1)]
    st.data_editor(df_l_disp, use_container_width=True, height=600, hide_index=True)

with t4:
    st.write("### ⚙️ Управление системой")
    if st.button("🔄 Обновить данные (Сбросить кэш)"):
        st.cache_data.clear()
        st.rerun()
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()
