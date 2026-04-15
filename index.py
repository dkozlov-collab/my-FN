import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="RBS: Мониторинг", layout="wide", page_icon="📊")

# Твоя актуальная ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    """Превращает любой мусор в таблице в чистое число"""
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except:
        return 0

def find_col(df, possible_names):
    """Ищет колонку в таблице, даже если в названии лишние пробелы"""
    for name in possible_names:
        for actual_col in df.columns:
            if name.lower().strip() == actual_col.lower().strip():
                return actual_col
    return None

@st.cache_data(ttl=15)
def load_data():
    try:
        df = pd.read_csv(URL).fillna(0)
        # Ограничиваемся первыми 85 строками, чтобы не цеплять мусор снизу
        df = df.head(85)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа к Google Таблице: {e}")
        return pd.DataFrame()

# --- ПУЛЬТ УПРАВЛЕНИЯ ---
st.markdown("<h1 style='text-align: center;'>💎 РЕГИСТРАЦИЯ ОБОРУДОВАНИЯ RBS</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Ищем важные колонки
    col_kkt = find_col(df_raw, ['Остатки ККТ', 'ККТ', 'Остаток ККТ'])
    col_partner = find_col(df_raw, ['Сервис Партнер', 'Партнер'])
    col_money = find_col(df_raw, ['Итого сумма', 'Итого', 'Сумма'])
    col_city = find_col(df_raw, ['Склад', 'Город'])

    # Чистим данные
    if col_kkt: df_raw[col_kkt] = df_raw[col_kkt].apply(clean_num)
    if col_money: df_raw[col_money] = df_raw[col_money].apply(clean_num)

    # --- ФИЛЬТРАЦИЯ ---
    st.sidebar.header("Фильтры")
    if col_partner:
        partners = ["ВСЕ ПАРТНЕРЫ"] + sorted([str(p) for p in df_raw[col_partner].unique() if p != 0 and p != "0"])
        sel_p = st.sidebar.selectbox("Выберите Партнера:", partners)
        df = df_raw[df_raw[col_partner] == sel_p] if sel_p != "ВСЕ ПАРТНЕРЫ" else df_raw
    else:
        df = df_raw

    # --- KPI ---
    c1, c2 = st.columns(2)
    total_kkt = df[col_kkt].sum() if col_kkt else 0
    c1.metric("📦 ВСЕГО ККТ", f"{total_kkt} шт")
    
    total_money = df[col_money].sum() if col_money else 0
    c2.metric("💰 КАПИТАЛ", f"{total_money:,.0f} ₽".replace(',', ' '))

    st.divider()

    # --- ГРАФИКИ ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### 🍩 Доли по складам")
        if col_kkt and col_city and total_kkt > 0:
            fig_pie = px.pie(df[df[col_kkt] > 0], values=col_kkt, names=col_city, hole=0.5)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Нет данных для круга")

    with col_r:
        st.write("### 📊 Наличие (Топ-10)")
        if col_kkt and col_city and total_kkt > 0:
            top_cities = df.nlargest(10, col_kkt)
            fig_bar = px.bar(top_cities, x=col_city, y=col_kkt, color=col_kkt, text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    # ТАБЛИЦА
    st.subheader("📋 Реестр данных")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ Таблица пуста. Проверь настройки доступа в Google Sheets (Доступ 'Все, у кого есть ссылка').")
