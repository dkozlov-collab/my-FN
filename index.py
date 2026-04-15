import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка для Pocophone
st.set_page_config(page_title="RBS: Склад", layout="wide")

# Дизайн
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    .total-box { background-color: #F0F8FF; padding: 15px; border-radius: 10px; border: 2px solid #007BFF; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКА (A:Q до 80 строки)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val) or val == "" or val == 0: return 0
        return int(float(str(val).replace(' ', '').replace('₽', '').replace(',', '.').replace('\xa0', '')))
    except: return 0

def find_col(df, keywords):
    for col in df.columns:
        if any(word.lower() in str(col).lower().strip() for word in keywords): return col
    return None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL).iloc[:80, 0:17].fillna(0)
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # 1. Сбор колонок
    c_city = find_col(df_raw, ['склад', 'город'])
    c_kkt  = find_col(df_raw, ['ккт', 'наличие'])
    c_fn15 = find_col(df_raw, ['фн-15', 'фн 15'])
    c_fn36 = find_col(df_raw, ['фн-36', 'фн 36'])
    c_money = find_col(df_raw, ['сумма', 'деньги'])
    c_spent = find_col(df_raw, ['расход', 'истратил'])

    # Чистка цифр
    for c in [c_kkt, c_fn15, c_fn36, c_money, c_spent]:
        if c: df_raw[c] = df_raw[c].apply(clean_num)

    # 2. МЕНЮ
    st.sidebar.title("УПРАВЛЕНИЕ")
    page = st.sidebar.radio("Раздел:", ["📊 Сводка", "📋 Таблица A:Q"])

    if page == "📊 Сводка":
        st.subheader("🏛️ ГЛОБАЛЬНЫЕ ОСТАТКИ")
        
        # Красивые итоги
        st.markdown("<div class='total-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("ОБОРОТ (₽)", f"{df_raw[c_money].sum() if c_money else 0:,.0f}".replace(',', ' '))
        col2.metric("ОСТАТОК ККТ", f"{df_raw[c_kkt].sum() if c_kkt else 0} шт")
        col3.metric("ВСЕГО ФН", f"{(df_raw[c_fn15].sum() if c_fn15 else 0) + (df_raw[c_fn36].sum() if c_fn36 else 0)} шт")
        st.markdown("</div>", unsafe_allow_html=True)

        # Таблица по городам
        if c_city:
            st.write("### 📍 По городам")
            summary = df_raw.groupby(c_city).agg({c_money:'sum', c_kkt:'sum', c_fn15:'sum', c_fn36:'sum'}).reset_index()
            st.dataframe(summary.sort_values(by=c_money, ascending=False), use_container_width=True, hide_index=True)

        # График
        if c_money and df_raw[c_money].sum() > 0:
            fig = px.pie(df_raw[df_raw[c_money]>0], values=c_money, names=c_city, hole=0.5, title="Доли оборота")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.subheader("📋 ПОЛНЫЙ РЕЕСТР")
        search = st.text_input("🔍 Поиск по таблице:")
        df_view = df_raw.copy()
        if search:
            df_view = df_view[df_view.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(df_view, use_container_width=True, hide_index=True)

else:
    st.error("Данные не загружены. Проверь доступ к таблице!")
