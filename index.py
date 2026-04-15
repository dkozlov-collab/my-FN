import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под Pocophone (Масштабный белый дизайн)
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 34px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Твоя ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.').replace('\xa0', '')
        return int(float(s))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        col_clean = str(col).lower().replace('\n', ' ').strip()
        if any(word.lower() in col_clean for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        # Читаем первые 100 строк, столбцы A-R
        df = pd.read_csv(URL).head(100).fillna(0)
        return df
    except: return pd.DataFrame()

st.markdown("<h1>🏛️ RBS: ЦЕНТР УПРАВЛЕНИЯ СТРУКТУРОЙ</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Динамический поиск колонок
    c_exit = find_col(df_raw, ['выезд', 'рег', 'тип'])
    c_sp   = find_col(df_raw, ['партнер', 'сервис'])
    c_city = find_col(df_raw, ['склад', 'город'])
    c_kkt  = find_col(df_raw, ['ккт', 'остатки'])
    c_spent = find_col(df_raw, ['истратил', 'расход'])
    c_money = find_col(df_raw, ['сумма', '15-фн', 'стоимость'])

    # Чистим весь массив цифр
    for col in [c_kkt, c_spent, c_money]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # --- ПУЛЬТ ФИЛЬТРОВ ---
    st.write("### 🛠️ Глобальные фильтры")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        e_list = sorted([str(x) for x in df_raw[c_exit].unique() if str(x) not in ['0', '']]) if c_exit else []
        sel_e = st.multiselect("Тип выезда", e_list)
    with f2:
        p_list = sorted([str(x) for x in df_raw[c_sp].unique() if str(x) not in ['0', '']]) if c_sp else []
        sel_p = st.multiselect("Выберите Партнера", p_list)
    with f3:
        c_list = sorted([str(x) for x in df_raw[c_city].unique() if str(x) not in ['0', '']]) if c_city else []
        sel_city = st.multiselect("Филиал / Город", c_list)

    # Применяем фильтры
    df = df_raw.copy()
    if sel_e: df = df[df[c_exit].astype(str).isin(sel_e)]
    if sel_p: df = df[df[c_sp].astype(str).isin(sel_p)]
    if sel_city: df = df[df[c_city].astype(str).isin(sel_city)]

    # --- ГЛАВНЫЕ МЕТРИКИ (СВОДКА) ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("ОБЩИЙ РАСХОД ФН", f"{df[c_spent].sum() if c_spent else 0} шт")
    m2.metric("ДЕНЕЖНЫЙ МАССИВ", f"{df[c_money].sum() if c_money else 0:,.0f} ₽".replace(',', ' '))
    m3.metric("ТЕКУЩИЙ ОСТАТОК ККТ", f"{df[c_kkt].sum() if c_kkt else 0} шт")

    # --- ГРАФИК РАСХОДА ---
    if c_city and c_spent and not df[df[c_spent]>0].empty:
        st.subheader("📈 Расход по филиалам")
        fig = px.bar(df[df[c_spent]>0].sort_values(c_spent, ascending=False), 
                     x=c_city, y=c_spent, text_auto=True, color_discrete_sequence=['#007BFF'])
        st.plotly_chart(fig, use_container_width=True)

    # --- ПОЛНАЯ ТАБЛИЦА (A:R) ---
    st.subheader("📋 Детальный реестр данных")
    st.dataframe(df.iloc[:, :18], use_container_width=True, hide_index=True)

else:
    st.error("Система не видит таблицу. Проверь доступ 'Все, у кого есть ссылка'!")
