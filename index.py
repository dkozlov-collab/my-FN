import streamlit as st
import pandas as pd
import re

# --- 1. СТИЛЬ ---
st.set_page_config(layout="wide", page_title="RBS TOTAL DATA")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 32px !important; font-weight: 800; }
    [data-testid="metric-container"] { border: 1px solid #DEE2E6; border-radius: 8px; padding: 15px; background-color: #F8F9FA; }
    .main-header { font-size: 28px; font-weight: 800; color: #1A237E; text-align: center; margin-bottom: 20px; }
    h3 { color: #1A237E; border-bottom: 2px solid #1A237E; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
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

# --- 3. ФИЛЬТРЫ ---
st.sidebar.header("⚙️ ГЛОБАЛЬНЫЙ ФИЛЬТР")
p_list = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Выберите партнеров:", [x for x in p_list if x not in ["", "0", "0.0"]])

df_s = df_s_raw.copy()
df_l = df_l_raw.copy()

if sel_p:
    df_s = df_s[df_s.iloc[:, 1].astype(str).isin(sel_p)]
    df_l = df_l[df_l.iloc[:, 1].astype(str).isin(sel_p)]

# --- 4. ВКЛАДКИ ---
st.markdown("<div class='main-header'>RBS: ЦИФРОВАЯ ПАНЕЛЬ УПРАВЛЕНИЯ</div>", unsafe_allow_html=True)
tab_a, tab_s, tab_l = st.tabs(["🔢 АНАЛИТИКА ПО СТОЛБЦАМ", "📦 ВЕСЬ СКЛАД", "🚚 ЛОГИСТИКА"])

with tab_a:
    st.write("### 📈 ИТОГИ ПО СКЛАДАМ И ПАРТНЕРАМ")
    
    # Краткие метрики
    c1, c2, c3 = st.columns(3)
    kkt_total = df_s.iloc[:, 5].apply(to_n).sum()
    fn_total = df_s.iloc[:, 6].apply(to_n).sum() + df_s.iloc[:, 7].apply(to_n).sum()
    money_total = df_l.iloc[:, 11].apply(to_n).sum()
    
    c1.metric("ККТ ВСЕГО", f"{int(kkt_total)} шт")
    c2.metric("ФН ВСЕГО", f"{int(fn_total)} шт")
    c3.metric("ЛОГИСТИКА", f"{int(money_total):,} ₽".replace(",", " "))

    st.divider()
    
    st.write("### 📊 ЦИФРЫ ПО ВСЕМ СТОЛБЦАМ СКЛАДА")
    # Создаем сводную таблицу: Партнер (1-й столб) и суммы по всем числовым столбцам (с 5-го по 80-й)
    if not df_s.empty:
        # Оставляем только нужные столбцы для анализа (Партнер + данные)
        cols_to_sum = df_s.columns[5:80]
        # Превращаем всё в числа для корректного сложения
        df_num = df_s.copy()
        for col in cols_to_sum:
            df_num[col] = df_num[col].apply(to_n)
            
        # Группируем по партнеру
        partner_col = df_s.columns[1]
        summary_table = df_num.groupby(partner_col)[cols_to_sum].sum().reset_index()
        
        # Выводим кликабельную таблицу с итогами по каждому столбцу
        st.data_editor(summary_table, use_container_width=True, hide_index=True)
    else:
        st.info("Нет данных для отображения")

with tab_s:
    st.write("### 📦 РЕЕСТР СКЛАДА (80 СТОЛБЦОВ)")
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

with tab_l:
    st.write("### 🚚 РЕЕСТР ЛОГИСТИКИ (5000 СТРОК)")
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)
