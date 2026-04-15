import streamlit as st
import pandas as pd
import plotly.express as px

# Масштабная настройка под Pocophone
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; }
</style>
""", unsafe_allow_html=True)

# Твоя новая рабочая ссылка
URL = "https://docs.google.com/spreadsheets/d/1m-HdbV_cEyJ5EW7OMyxkpuDgDgPajfnwgi7rvnm7hcE/export?format=csv"

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
def load_massive_data():
    try:
        # ЗАДАЧА: С А по R (18 столбцов), до 80 строки
        df = pd.read_csv(URL).iloc[:80, :18].fillna(0)
        return df
    except: return pd.DataFrame()

st.markdown("<h1>📊 RBS: МАССИВ АНАЛИЗА (A:R)</h1>", unsafe_allow_html=True)

df_raw = load_massive_data()

if not df_raw.empty:
    # 1. ПОИСК ЗАГОЛОВКОВ ДЛЯ АНАЛИЗА
    c_spent = find_col(df_raw, ['истратил', 'расход', 'отправлено'])
    c_money = find_col(df_raw, ['сумма', 'денежн', 'стоимость'])
    c_kkt   = find_col(df_raw, ['ккт', 'остатки', 'наличие'])
    c_city  = find_col(df_raw, ['склад', 'город', 'филиал'])
    c_exit  = find_col(df_raw, ['выезд', 'тип'])
    c_sp    = find_col(df_raw, ['партнер', 'сервис'])

    # Чистим массив цифр
    for c in [c_spent, c_money, c_kkt]:
        if c: df_raw[c] = df_raw[c].apply(clean_num)

    # 2. ПУЛЬТ УПРАВЛЕНИЯ (ФИЛЬТРЫ)
    st.write("### 🛠️ Настройка анализа")
    f1, f2, f3 = st.columns(3)
    with f1:
        e_list = ["Все"] + sorted([str(x) for x in df_raw[c_exit].unique() if str(x) != '0']) if c_exit else ["Все"]
        sel_e = st.selectbox("Тип выезда", e_list)
    with f2:
        p_list = ["Все"] + sorted([str(x) for x in df_raw[c_sp].unique() if str(x) != '0']) if c_sp else ["Все"]
        sel_p = st.selectbox("Сервис-Партнер", p_list)
    with f3:
        c_list = ["Все"] + sorted([str(x) for x in df_raw[c_city].unique() if str(x) != '0']) if c_city else ["Все"]
        sel_c = st.selectbox("Город / Склад", c_list)

    # Применяем фильтры
    df = df_raw.copy()
    if sel_e != "Все": df = df[df[c_exit].astype(str) == sel_e]
    if sel_p != "Все": df = df[df[c_sp].astype(str) == sel_p]
    if sel_c != "Все": df = df[df[c_city].astype(str) == sel_c]

    # 3. ГЛАВНЫЕ ЗАГОЛОВКИ (ИТОГИ)
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("РАСХОД ФН", f"{df[c_spent].sum() if c_spent else 0} шт")
    m2.metric("СУММА (ДЕНЬГИ)", f"{df[c_money].sum() if c_money else 0:,.0f} ₽".replace(',', ' '))
    m3.metric("ОСТАТОК ККТ", f"{df[c_kkt].sum() if c_kkt else 0} шт")

    # 4. КРАСИВЫЕ КРУГЛЫЕ ГРАФИКИ
    st.divider()
    g1, g2 = st.columns(2)
    
    with g1:
        if c_spent and df[df[c_spent]>0].any().any():
            fig_fn = px.pie(df[df[c_spent]>0], values=c_spent, names=c_city if c_city else c_sp, 
                            hole=0.5, title="🔵 Расход ФН (доли)")
            st.plotly_chart(fig_fn, use_container_width=True)
            
    with g2:
        if c_kkt and df[df[c_kkt]>0].any().any():
            fig_kkt = px.pie(df[df[c_kkt]>0], values=c_kkt, names=c_city if c_city else c_sp, 
                             hole=0.5, title="🟢 Наличие ККТ (доли)")
            st.plotly_chart(fig_kkt, use_container_width=True)
            # 5. ГЛАВНЫЙ МАССИВ (ТАБЛИЦА)
    st.write("### 📋 Полный реестр структуры (A:R)")
    # Позволяет открывать ссылки прямо из таблицы
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("Жду данные... Дима, проверь доступ в Google Таблице!")
