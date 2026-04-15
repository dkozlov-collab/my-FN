import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Настройка футуристичного интерфейса 2026
st.set_page_config(page_title="RBS Global: Total Analytics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 0 0 10px #00E5FF; }
    .filter-box { border: 1px solid #00E5FF; padding: 15px; border-radius: 10px; background-color: #161A24; }
</style>
""", unsafe_allow_html=True)

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    for c in df.columns:
        if key.lower() in c.replace('\n', ' ').lower(): return c
    return None

@st.cache_data(ttl=10)
def load_full_stock():
    try:
        # Читаем склад (1-80) и анализируем ВСЕ столбцы
        df = pd.read_csv(URL).head(80).fillna(0)
        return df
    except: return pd.DataFrame()

# --- ГЛАВНЫЙ ЭКРАН ---
st.markdown("<h1 style='text-align: center;'>📡 RBS: TOTAL WAREHOUSE ANALYTICS</h1>", unsafe_allow_html=True)

df_raw = load_full_stock()

if not df_raw.empty:
    # --- БЛОК УМНЫХ ФИЛЬТРОВ ---
    st.sidebar.header("🎯 Глобальные Фильтры")
    
    # Ищем колонки для фильтрации
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_kkt = find_col(df_raw, 'ККТ')
    c_sum = find_col(df_raw, 'Сумма')

    # Очистка числовых данных по всей таблице
    for col in df_raw.columns:
        if any(word in col.lower() for word in ['ккт', 'сумма', 'фн', 'шт', 'руб']):
            df_raw[col] = df_raw[col].apply(clean_num)

    # Список для фильтра
    all_partners = ["ВСЕ ПАРТНЕРЫ"] + sorted([str(p) for p in df_raw[c_sp].unique() if p != 0])
    sel_p = st.sidebar.selectbox("Выберите Сервис-Партнера:", all_partners)

    # Применяем фильтрацию к данным
    df_filtered = df_raw.copy()
    if sel_p != "ВСЕ ПАРТНЕРЫ":
        df_filtered = df_filtered[df_filtered[c_sp] == sel_p]

    # --- ВИЗУАЛИЗАЦИЯ (СИНХРОННАЯ) ---
    col1, col2, col3 = st.columns(3)
    
    total_kkt = df_filtered[c_kkt].sum() if c_kkt else 0
    total_money = df_filtered[c_sum].sum() if c_sum else 0
    
    col1.metric("📦 ККТ (ФИЛЬТР)", f"{total_kkt} шт")
    col2.metric("💰 СУММА (ФИЛЬТР)", f"{total_money:,.0f} ₽".replace(',', ' '))
    col3.metric("📍 ЛОКАЦИЙ", len(df_filtered[df_filtered[c_kkt] > 0]))

    st.divider()

    # ГРАФИКИ, КОТОРЫЕ МЕНЯЮТСЯ ОТ ФИЛЬТРА
    g1, g2 = st.columns(2)
    
    with g1:
        st.write("### 🍩 Доли внутри выборки")
        if total_kkt > 0 and c_sp:
            fig_pie = px.pie(df_filtered[df_filtered[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.6)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with g2:
        st.write("### 📊 Распределение по городам")
        if c_city and total_kkt > 0:
            fig_bar = px.bar(df_filtered.nlargest(10, c_kkt), x=c_city, y=c_kkt, color=c_kkt, text_auto=True)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- ВЫТЯНУТАЯ СТРОКА (ВСЕ СТОЛБЦЫ) ---
    st.write("### 📋 Полная аналитическая строка (Все столбцы таблицы)")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

else:
    st.error("Ошибка! Проверь доступ к Google Таблице (кнопка 'Поделиться').")
