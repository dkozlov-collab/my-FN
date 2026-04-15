import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под твой телефон (Масштабный белый дизайн)
st.set_page_config(page_title="RBS: Глобальный Массив", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 3px solid #007BFF; padding-bottom: 10px; }
    .total-line { background-color: #F0F8FF; padding: 15px; border-radius: 10px; border: 2px solid #007BFF; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

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
        # ЗАДАЧА: А:R до 80 строки
        df = pd.read_csv(URL).iloc[:80, :18].fillna(0)
        return df
    except: return pd.DataFrame()

st.markdown("<h1>🏛️ RBS: ЦЕНТР УПРАВЛЕНИЯ</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Ищем колонки для итоговой строки
    c_sp    = find_col(df_raw, ['партнер', 'сервис'])
    c_city  = find_col(df_raw, ['склад', 'город'])
    c_kkt   = find_col(df_raw, ['остатки ккт', 'наличие ккт', 'ккт'])
    c_fn15  = find_col(df_raw, ['фн-15', 'фн 15'])
    c_fn36  = find_col(df_raw, ['фн-36', 'фн 36'])
    c_sim   = find_col(df_raw, ['sim', 'сим'])
    c_spent = find_col(df_raw, ['расход', 'истратил'])

    # Чистим данные (защита от TypeError)
    for col in [c_kkt, c_fn15, c_fn36, c_sim, c_spent]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # --- ФИЛЬТРЫ ---
    st.write("### 🔍 Фильтрация")
    f1, f2 = st.columns(2)
    with f1:
        sp_list = sorted([str(x) for x in df_raw[c_sp].unique() if str(x) not in ['0', '']]) if c_sp else []
        sel_sp = st.multiselect("Выберите Партнера", sp_list)
    with f2:
        city_list = sorted([str(x) for x in df_raw[c_city].unique() if str(x) not in ['0', '']]) if c_city else []
        sel_city = st.multiselect("Выберите Город", city_list)

    df = df_raw.copy()
    if sel_sp: df = df[df[c_sp].astype(str).isin(sel_sp)]
    if sel_city: df = df[df[c_city].astype(str).isin(sel_city)]

    # --- ТАБЛИЦА ---
    st.write("### 📋 Остатки (A:Q)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- ОСТАТКИ В СТРОКУ (ИТОГИ) ---
    st.markdown("<div class='total-line'>", unsafe_allow_html=True)
    st.subheader("🏁 ИТОГО ОСТАЛОСЬ:")
    
    # Все цифры в один ряд
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.metric("ККТ", f"{df[c_kkt].sum() if c_kkt else 0} шт")
    with t2:
        st.metric("ФН-15", f"{df[c_fn15].sum() if c_fn15 else 0} шт")
    with t3:
        st.metric("ФН-36", f"{df[c_fn36].sum() if c_fn36 else 0} шт")
    with t4:
    st.markdown("</div>", unsafe_allow_html=True)

    # --- КРУГЛЫЙ ГРАФИК ---
    if c_spent and df[df[c_spent]>0].any().any():
        st.divider()
        fig = px.pie(df[df[c_spent]>0], values=c_spent, names=c_city if c_city else c_sp, 
                     hole=0.5, title="🔵 Доли расходов")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Ошибка: Проверь доступ к Google Таблице!")
