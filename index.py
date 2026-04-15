import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. СТИЛЬ (NEON DARK) ---
st.set_page_config(layout="wide", page_title="RBS TOTAL CONTROL")

st.markdown("""
<style>
    .stApp { background-color: #050c1a; color: #e0e6ed; }
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 30px !important; font-weight: bold; text-shadow: 0 0 10px #00f2fe; }
    [data-testid="metric-container"] { background: #0a1e3c; border: 1px solid #00f2fe; border-radius: 12px; padding: 15px; }
    h1, h2 { text-align: center; color: #00f2fe; text-transform: uppercase; text-shadow: 0 0 15px #00f2fe; }
    .stDataFrame { border: 1px solid #00f2fe; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ДАННЫЕ (РУЧНАЯ ЗАГРУЗКА) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def parse_n(val):
    try:
        nums = re.findall(r'\d+', str(val).replace(' ', ''))
        return float(nums[0]) if nums else 0.0
    except: return 0.0

@st.cache_data(ttl=5)
def load():
    s = pd.read_csv(S_URL).iloc[:500, 0:80].fillna("")
    l = pd.read_csv(L_URL).iloc[:1000, 0:80].fillna("")
    return s, l

df_s_raw, df_l_raw = load()

# --- 3. ГЛОБАЛЬНЫЙ ФИЛЬТР ---
st.sidebar.title("💎 RBS ВЕРИФИКАЦИЯ")
partners = sorted(list(set(df_s_raw.iloc[:, 1].astype(str)) | set(df_l_raw.iloc[:, 1].astype(str))))
sel_p = st.sidebar.multiselect("Выберите партнера:", [x for x in partners if x not in ["", "0", "0.0"]])

df_s = df_s_raw[df_s_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_s_raw
df_l = df_l_raw[df_l_raw.iloc[:, 1].astype(str).isin(sel_p)] if sel_p else df_l_raw

# --- 4. ВКЛАДКИ ---
t1, t2, t3, t4 = st.tabs(["📊 ДАШБОРД", "📋 СКЛАД (ДЕТАЛИ)", "🚚 ЛОГИСТИКА", "📉 ГРАФИКИ СПИСАНИЯ"])

with t1:
    st.markdown("<h1>ГЛОБАЛЬНЫЕ ОСТАТКИ</h1>", unsafe_allow_html=True)
    
    # Расчеты остатков
    kkt_now = df_s.iloc[:, 5].apply(parse_n).sum() # В наличии
    fn_now = df_s.iloc[:, 6].apply(parse_n).sum() + df_s.iloc[:, 7].apply(parse_n).sum()
    
    # Расчет списания (Столбцы 9 и 10 - пример списания)
    # Если у тебя списание в других столбцах, просто поменяй индексы (8, 9)
    kkt_off = df_s.iloc[:, 8].apply(parse_n).sum() 
    
    c1, c2, c3 = st.columns(3)
    c1.metric("КАССЫ В НАЛИЧИИ", f"{int(kkt_now)} шт")
    c2.metric("ФН В НАЛИЧИИ", f"{int(fn_now)} шт")
    c3.metric("ВСЕГО СПИСАНО", f"{int(kkt_off)} шт", delta_color="inverse")

    st.divider()
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.write("### Остатки по городам")
        fig_sklad = px.pie(df_s, values=df_s.columns[5], names=df_s.columns[2], hole=0.5)
        fig_sklad.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_sklad, use_container_width=True)
    
    with col_r:
        st.write("### Обязательства (Деньги)")
        money = df_l.iloc[:, 11].apply(parse_n).sum()
        m_str = f"{int(money):,}".replace(",", " ")
        st.metric("СУММА К ОПЛАТЕ", f"{m_str} ₽")
        fig_money = px.pie(df_l, values=df_l.iloc[:, 11].apply(parse_n), names=df_l.columns[1], hole=0.5)
        fig_money.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_money, use_container_width=True)

with t2:
    st.write("### 📋 Полный реестр склада (Все 80 столбцов)")
    # Выводим остатки по каждому столбцу, где есть числа
    st.dataframe(df_s, use_container_width=True)

with t3:
    st.write("### 🚚 Логистика и посылки")
    search = st.text_input("🔍 Поиск по серийнику/городу:")
    if search:
        df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df_l, use_container_width=True)
with t4:
    st.markdown("<h1>📉 АНАЛИТИКА СПИСАНИЯ</h1>", unsafe_allow_html=True)
    
    # График списания по партнерам
    df_off = df_s.copy()
    df_off['СПИСАНО'] = df_off.iloc[:, 8].apply(parse_n) # Допустим, 9-й столбец - это списание
    
    fig_off = px.bar(df_off, x=df_off.columns[1], y='СПИСАНО', color=df_off.columns[2], 
                     title="Количество списанного оборудования по партнерам")
    fig_off.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_off, use_container_width=True)
    
    st.write("### Список списанных позиций")
    st.table(df_off[df_off['СПИСАНО'] > 0][[df_off.columns[1], df_off.columns[2], 'СПИСАНО']])
