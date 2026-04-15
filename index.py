import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка стиля 2026 (Темная тема + Неон)
st.set_page_config(page_title="RBS: Аналитика Склада", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; }
    .stDataFrame { border: 1px solid #444; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Твоя рабочая ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    """Ищет колонку, игнорируя регистр и переносы строк"""
    for c in df.columns:
        if key.lower() in c.replace('\n', ' ').lower():
            return c
    return None

@st.cache_data(ttl=15)
def load_stock_data():
    try:
        # Читаем строго первые 80 строк для склада
        df = pd.read_csv(URL).head(80).fillna(0)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа: {e}")
        return pd.DataFrame()

# ЗАГОЛОВОК
st.markdown("<h1 style='text-align: center;'>🏙️ АНАЛИТИКА СКЛАДА 2026</h1>", unsafe_allow_html=True)

df = load_stock_data()

if not df.empty:
    # Ищем ключевые колонки
    c_kkt = find_col(df, 'Остатки ККТ')
    c_sum = find_col(df, 'Сумма')
    c_sp = find_col(df, 'Партнер')
    c_city = find_col(df, 'Склад')

    if c_kkt:
        df[c_kkt] = df[c_kkt].apply(clean_num)
        total_kkt = df[c_kkt].sum()
        
        # КРУПНЫЕ ЦИФРЫ СВЕРХУ (как на фото)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("📦 ВСЕГО ККТ НА СКЛАДАХ", f"{total_kkt} шт")
        with col_m2:
            if c_sum:
                df[c_sum] = df[c_sum].apply(clean_num)
                st.metric("💰 ОБЩИЙ КАПИТАЛ", f"{df[c_sum].sum():,.0f} ₽".replace(',', ' '))

        st.divider()

        # ГРАФИКИ (Твоя красота)
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.write("### 🍩 Доли Партнеров (АБ, ТМ и др.)")
            if c_sp and total_kkt > 0:
                fig = px.pie(df[df[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.65)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        with col_r:
            st.write("### 📈 Наличие по Городам")
            if c_city:
                # Берем только те города, где есть ККТ
                top_cities = df[df[c_kkt] > 0].nlargest(12, c_kkt)
                fig_bar = px.bar(top_cities, x=c_city, y=c_kkt, color=c_kkt, text_auto=True)
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.write("### 📋 Полный реестр остатков (1-80)")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("Проверь доступ в Google Таблице (кнопка Поделиться)!")
