import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка интерфейса под мобильный
st.set_page_config(page_title="RBS: Финансы и Остатки", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; }
    .main-title { color: #1A237E; text-align: center; font-weight: bold; border-bottom: 2px solid #007BFF; }
    .section-box { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border-left: 5px solid #007BFF; margin-bottom: 20px; }
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
        # Берем массив A:R (18 столбцов)
        df = pd.read_csv(URL).iloc[:80, :18].fillna(0)
        return df
    except: return pd.DataFrame()

st.markdown("<h1 class='main-title'>🏛️ RBS: ОБОРОТ И ОСТАТКИ</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Определяем ключевые колонки
    c_city  = find_col(df_raw, ['склад', 'город'])
    c_kkt   = find_col(df_raw, ['остатки ккт', 'наличие ккт', 'ккт'])
    c_fn15  = find_col(df_raw, ['фн-15', 'фн 15'])
    c_fn36  = find_col(df_raw, ['фн-36', 'фн 36'])
    c_money = find_col(df_raw, ['сумма', 'стоимость', 'деньги'])
    c_spent = find_col(df_raw, ['расход', 'истратил'])

    # Чистим цифры во всем массиве
    num_cols = [c_kkt, c_fn15, c_fn36, c_money, c_spent]
    for col in num_cols:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # --- БЛОК 1: ГЛАВНЫЕ ЦИФРЫ (ОБОРОТ) ---
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💰 Финансовый результат")
    col1, col2 = st.columns(2)
    total_money = df_raw[c_money].sum() if c_money else 0
    total_spent = df_raw[c_spent].sum() if c_spent else 0
    col1.metric("ОБЩИЙ ОБОРОТ (₽)", f"{total_money:,.0f}".replace(',', ' '))
    col2.metric("РАСХОД ФН (ШТ)", f"{total_spent} шт")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- БЛОК 2: АНАЛИТИКА ПО ФИЛИАЛАМ ---
    st.write("### 📍 Остатки и деньги по городам")
    if c_city:
        # Группируем всё по городу
        summary = df_raw.groupby(c_city).agg({
            c_money: 'sum',
            c_kkt: 'sum',
            c_fn15: 'sum',
            c_fn36: 'sum'
        }).reset_index()
        
        # Переименуем для красоты
        summary.columns = ['Филиал', 'Оборот ₽', 'ККТ', 'ФН-15', 'ФН-36']
        st.dataframe(summary.sort_values(by='Оборот ₽', ascending=False), use_container_width=True, hide_index=True)

    # --- БЛОК 3: ГРАФИК ДЕНЕГ ---
    st.divider()
    if c_money and total_money > 0:
        fig = px.pie(summary[summary['Оборот ₽'] > 0], values='Оборот ₽', names='Филиал', 
                     hole=0.4, title="📊 Распределение оборота по филиалам")
        st.plotly_chart(fig, use_container_width=True)

    # --- БЛОК 4: ПОЛНЫЙ МАССИВ ---
    with st.expander("🔍 Посмотреть весь массив данных (A:R)"):
        st.dataframe(df_raw, use_container_width=True)

else:
    st.error("Данные не загружены. Проверь доступ к Google Таблице!")
