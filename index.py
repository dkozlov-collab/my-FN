import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под Pocophone (Масштабный белый дизайн)
st.set_page_config(page_title="RBS: Склад и Финансы", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 32px; font-weight: bold; }
    .total-box { background-color: #F0F8FF; padding: 20px; border-radius: 15px; border: 2px solid #007BFF; margin-bottom: 20px; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКА (Диапазон A:Q, до 80 строки)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.').replace('\xa0', '')
        return int(float(s))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        col_clean = str(col).lower().strip()
        if any(word.lower() in col_clean for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        # Четко берем столбцы A-Q (0:17) и 80 строк
        df = pd.read_csv(URL).iloc[:80, 0:17].fillna(0)
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # 1. АВТОПОИСК КОЛОНОК
    c_city  = find_col(df_raw, ['склад', 'город'])
    c_kkt   = find_col(df_raw, ['ккт', 'наличие'])
    c_fn15  = find_col(df_raw, ['фн-15', 'фн 15'])
    c_fn36  = find_col(df_raw, ['фн-36', 'фн 36'])
    c_money = find_col(df_raw, ['сумма', 'стоимость', 'деньги'])
    c_spent = find_col(df_raw, ['расход', 'истратил'])
    c_sp    = find_col(df_raw, ['партнер', 'сервис'])

    # Чистим цифры
    for col in [c_kkt, c_fn15, c_fn36, c_money, c_spent]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # 2. МЕНЮ СЛЕВА
    st.sidebar.header("📦 УПРАВЛЕНИЕ RBS")
    page = st.sidebar.radio("Перейти в раздел:", ["🏠 Главный Монитор", "📍 Сводка по Городам", "📋 Весь массив (A:Q)"])

    if page == "🏠 Главный Монитор":
        st.markdown("<h1>🏛️ ГЛОБАЛЬНЫЙ МОНИТОРИНГ</h1>", unsafe_allow_html=True)
        
        # Основные цифры сверху
        st.markdown("<div class='total-box'>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("ОБОРОТ (₽)", f"{df_raw[c_money].sum() if c_money else 0:,.0f}".replace(',', ' '))
        m2.metric("ОСТАТОК ККТ", f"{df_raw[c_kkt].sum() if c_kkt else 0} шт")
        m3.metric("РАСХОД ФН", f"{df_raw[c_spent].sum() if c_spent else 0} шт")
        st.markdown("</div>", unsafe_allow_html=True)

        # Круглый график (Бублик)
        if c_money and df_raw[c_money].sum() > 0:
            fig = px.pie(df_raw[df_raw[c_money]>0], values=c_money, names=c_city if c_city else c_sp, 
                         hole=0.5, title="🔵 Доли оборота по филиалам")
            st.plotly_chart(fig, use_container_width=True)

    elif page == "📍 Сводка по Городам":
        st.markdown("<h1>📍 АНАЛИТИКА ФИЛИАЛОВ</h1>", unsafe_allow_html=True)
        if c_city:
            # Группируем остатки и деньги по городу
            summary = df_raw.groupby(c_city).agg({
                c_money: 'sum',
                c_kkt: 'sum',
                c_fn15: 'sum',
                c_fn36: 'sum'
            }).reset_index()
            summary.columns = ['Город/Склад', 'Деньги (₽)', 'ККТ (шт)', 'ФН-15', 'ФН-36']
            st.dataframe(summary.sort_values(by='Деньги (₽)', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("Колонка 'Город' не найдена")

    elif page == "📋 Весь массив (A:Q)":
        st.markdown("<h1>📋 РЕЕСТР ДАННЫХ</h1>", unsafe_allow_html=True)
search = st.text_input("🔍 Быстрый поиск (введи город, серийник или партнера):")
        
        df_display = df_raw.copy()
        if search:
            df_display = df_display[df_display.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)

else:
    st.error("Ошибка загрузки! Дима, проверь доступ к таблице.")
