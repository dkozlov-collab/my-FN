import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ И ДИЗАЙН ---
st.set_page_config(layout="wide", page_title="RBS TOTAL CONTROL 2026")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E9ECEF; }
    .main-header { font-size: 28px; font-weight: 800; color: #1A237E; margin-bottom: 20px; }
    [data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E9ECEF; border-radius: 12px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА ДОСТУПОВ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"},
    "br": {"pass": "br123", "partner": "БР"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 3. АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 0.8, 1])
    with col_log:
        st.markdown("<h2 style='text-align: center;'>🔐 RBS ВХОД</h2>", unsafe_allow_html=True)
        u = st.text_input("Логин").lower().strip()
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            if u in USER_DB and USER_DB[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u]["partner"]
                st.rerun()
            else: st.error("Ошибка доступа")
    st.stop()

# --- 4. ЗАГРУЗКА ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        n = re.findall(r'[-+]?\d*\.?\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=10)
def load_data():
    try:
        s = pd.read_csv(S_URL).iloc[:, 0:80].fillna(0)
        l = pd.read_csv(L_URL).iloc[:5000, 0:80].fillna(0)
        s = s[~s.iloc[:, 1].astype(str).str.strip().isin(["0", "0.0", "", "СП", "Партнер"])]
        l = l[~l.iloc[:, 1].astype(str).str.strip().isin(["0", "0.0", ""])]
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s_raw, df_l_raw = load_data()

# --- 5. ЛЕВОЕ МЕНЮ (САЙДБАР) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_role}")
    st.divider()
    menu = st.radio("МЕНЮ СИСТЕМЫ:", ["🔢 АНАЛИТИКА", "📦 СКЛАД (80 СТ)", "🚚 ЛОГИСТИКА"])
    st.divider()
    
    role = st.session_state.user_role
    if role == "ALL":
        p_opts = sorted(df_s_raw.iloc[:, 1].unique().astype(str))
        sel_p = st.multiselect("ФИЛЬТР ПАРТНЕРОВ:", p_opts)
        df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
        df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
    else:
        df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
        df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

    if st.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

# --- 6. ОСНОВНОЙ КОНТЕНТ ---
st.markdown(f"<div class='main-header'>{menu}</div>", unsafe_allow_html=True)

if menu == "🔢 АНАЛИТИКА":
    c1, c2, c3 = st.columns(3)
    kkt = df_s.iloc[:, 5].apply(to_n).sum()
    fn_all = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    c1.metric("ККТ ВСЕГО", f"{int(kkt)} шт")
    c2.metric("ФН ВСЕГО", f"{int(fn_all)} шт")
    c3.metric("ПАРТНЕРОВ", f"{len(df_s.iloc[:, 1].unique())}")

    st.write("### Сводная таблица (Итоги)")
    map_cols = {
        df_s.columns[1]: "ПАРТНЕР", df_s.columns[3]: "План", df_s.columns[4]: "Мин.ост",
        df_s.columns[5]: "ККТ", df_s.columns[6]: "ФН-15", df_s.columns[7]: "ФН-36",
        df_s.columns[8]: "SIM", df_s.columns[9]: "В пути",
        df_s.columns[10]: "Расход 15", df_s.columns[11]: "Расход 36"
    }
    df_c = df_s.copy()
    for c in list(map_cols.keys())[1:]: df_c[c] = df_c[c].apply(to_n)
    summ = df_c.groupby(df_s.columns[1])[list(map_cols.keys())[1:]].sum().reset_index()
    summ.rename(columns=map_cols, inplace=True)
    
    total = summ.sum(numeric_only=True).to_frame().T
    total["ПАРТНЕР"] = "ОБЩИЙ ИТОГ"
    summ = pd.concat([summ, total], ignore_index=True)
    st.data_editor(summ, use_container_width=True, hide_index=True)

elif menu == "📦 СКЛАД (80 СТ)":
    search_s = st.text_input("🔍 Поиск по складу:")
    if search_s:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    st.data_editor(df_s, use_container_width=True, height=700, hide_index=True)

elif menu == "🚚 ЛОГИСТИКА":
    # --- НОВЫЙ ФИЛЬТР ПОЛУЧАТЕЛЯ ---
    # Предположим, что Получатель находится в 5-м столбце (индекс 4) логистики
    # Если столбец другой, просто поменяй индекс [4] ниже
    recipient_col = df_l.columns[4] 
    recipients = sorted([str(x) for x in df_l[recipient_col].unique() if str(x) not in ["0", "0.0", ""]])
    
    col1, col2 = st.columns([1, 2])
    with col1:
        sel_recipient = st.selectbox("👤 Фильтр: Получатель", ["Все"] + recipients)
    with col2:
        search_l = st.text_input("🔍 Поиск по ТТН / Комментарию:")

    if sel_recipient != "Все":
        df_l = df_l[df_l[recipient_col].astype(str) == sel_recipient]
    if search_l:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]

    st.data_editor(df_l, use_container_width=True, height=700, hide_index=True)
