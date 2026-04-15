import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ---
st.set_page_config(layout="wide", page_title="RBS GLOBAL SYSTEM")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 15px; background-color: #F8F9FA; }
    .main-header { font-size: 24px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
USER_DB = {
    "admin": {"pass": "admin777", "partner": "ALL"},
    "ab1": {"pass": "ab2026", "partner": "АБ"},
    "atml": {"pass": "atmgo", "partner": "ATM"}
}

# --- 3. ВХОД (ИСПРАВИЛ ОШИБКУ С РЕГИСТРОМ) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 ВХОД В RBS SYSTEM</h1>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        u = st.text_input("Логин (пиши маленькими: admin)")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            u_check = u.lower().strip() # Теперь Admin и admin сработают одинаково
            if u_check in USER_DB and USER_DB[u_check]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user_role = USER_DB[u_check]["partner"]
                st.rerun()
            else:
                st.error("❌ Неверный логин или пароль")
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

# --- 5. ФИЛЬТРАЦИЯ ---
role = st.session_state.user_role
if role == "ALL":
    st.sidebar.success("РЕЖИМ: АДМИНИСТРАТОР")
    p_list = sorted([x for x in df_s_raw.iloc[:, 1].unique() if str(x) not in ["0", "0.0", ""]])
    sel_p = st.sidebar.multiselect("Выберите партнера:", p_list)
    df_s = df_s_raw[df_s_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_s_raw
    df_l = df_l_raw[df_l_raw.iloc[:, 1].isin(sel_p)] if sel_p else df_l_raw
else:
    df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]
    df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).str.contains(role, case=False)]

# --- 6. КОНТЕНТ (БЕЗ ЛИШНЕЙ СТРОКИ) ---
st.markdown(f"<div class='main-header'>RBS GLOBAL: {role}</div>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🔢 АНАЛИТИКА", "📦 СКЛАД", "🚚 ЛОГИСТИКА"])

with t1:
    st.write("### 📊 Сводные данные")
    
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
    for c in list(cols_map.keys())[1:]:
        df_calc[c] = df_calc[c].apply(to_n)
        
    # УДАЛЯЕМ ЛИШНЮЮ СТРОКУ "0" ПЕРЕД ГРУППИРОВКОЙ
    df_calc = df_calc[df_calc.iloc[:, 1].astype(str).str.strip() != "0"]
    df_calc = df_calc[df_calc.iloc[:, 1].astype(str).str.strip() != ""]
    
    summary = df_calc.groupby(df_s.columns[1])[list(cols_map.keys())[1:]].sum().reset_index()
    summary.rename(columns=cols_map, inplace=True)
    
    # ИТОГО
    itogo = summary.sum(numeric_only=True).to_frame().T
    itogo["ПАРТНЕР"] = "ИТОГО"
    summary = pd.concat([summary, itogo], ignore_index=True)
    
    # МЕТРИКИ
    m1, m2, m3 = st.columns(3)
    m1.metric("ККТ ВСЕГО", f"{int(itogo['ККТ'].iloc[0])} шт")
    m2.metric("ФН ВСЕГО", f"{int(itogo['ФН-15'].iloc[0] + itogo['ФН-36'].iloc[0])} шт")
    # Считаем логистику (11-й столбец)
    money_log = df_l.iloc[:, 11].apply(to_n).sum()
    m3.metric("ЛОГИСТИКА", f"{int(money_log):,} ₽".replace(",", " "))

    st.divider()
    st.data_editor(summary, use_container_width=True, hide_index=True)

with t2:
    st.data_editor(df_s, use_container_width=True, height=500, hide_index=True)

with t3:
    st.data_editor(df_l, use_container_width=True, height=500, hide_index=True)

if st.sidebar.button("ВЫЙТИ"):
    st.session_state.auth = False
    st.rerun()

# 3. Выводим уже отфильтрованную таблицу
st.data_editor(df_filtered, use_container_width=True, height=600)
# --- БЛОК ПРОДВИНУТОЙ ФИЛЬТРАЦИИ ПО СТОЛБЦАМ ---
st.write("### 🛠 Фильтры по столбцам")

# Создаем копию данных для фильтрации (df — это твоя переменная с данными)
df_filtered = df.copy()

# Выбираем столбцы, по которым хочешь фильтровать (например, первые 10)
columns_to_filter = df.columns[:10] 

# Создаем горизонтальные колонки для фильтров
cols = st.columns(len(columns_to_filter))

for i, col_name in enumerate(columns_to_filter):
    with cols[i]:
        # Собираем уникальные значения в столбце
        unique_vals = sorted(df[col_name].unique().astype(str))
        # Добавляем вариант "Все", чтобы фильтр не срабатывал сразу
        selected_val = st.selectbox(f"{col_name}", ["Все"] + unique_vals, key=f"filter_{col_name}")
        
        if selected_val != "Все":
            df_filtered = df_filtered[df_filtered[col_name].astype(str) == selected_val]

st.divider()

# Теперь выводим отфильтрованную таблицу
st.data_editor(df_filtered, use_container_width=True, height=600, hide_index=True)
