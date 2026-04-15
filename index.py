import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка стиля 2026
st.set_page_config(page_title="RBS: Регистрация", layout="wide", page_icon="💎")

# Твоя новая ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        # Убираем лишние символы и конвертируем в число
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except:
        return 0

@st.cache_data(ttl=15)
def load_data():
    try:
        # Читаем только массив регистрации (первые 80 строк)
        df = pd.read_csv(URL).head(80).fillna(0)
        
        # Чистим основные колонки
        cols_to_fix = ['Остатки ККТ', 'Итого сумма', 'Остатки ФН-15', 'Остатки ФН-36']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = df[col].apply(clean_num)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа к таблице: {e}")
        return pd.DataFrame()

# ЗАГОЛОВОК С ПЕРЧИНКОЙ
st.markdown("<h1 style='text-align: center; color: #00E5FF;'>💎 РЕГИСТРАЦИЯ ОБОРУДОВАНИЯ RBS</h1>", unsafe_allow_html=True)

df = load_data()

if not df.empty:
    # --- БОКОВАЯ ПАНЕЛЬ (УПРАВЛЕНИЕ) ---
    st.sidebar.header("⚙️ Фильтры")
    
    # Динамический фильтр по партнерам
    if 'Сервис Партнер' in df.columns:
        partners = ["ВСЕ ПАРТНЕРЫ"] + sorted([str(p) for p in df['Сервис Партнер'].unique() if p != 0])
        sel_p = st.sidebar.selectbox("🎯 Выберите Партнера:", partners)
        
        if sel_p != "ВСЕ ПАРТНЕРЫ":
            df = df[df['Сервис Партнер'] == sel_p]

    # --- ГЛАВНЫЕ ПОКАЗАТЕЛИ ---
    c1, c2, c3 = st.columns(3)
    
    total_kkt = df['Остатки ККТ'].sum()
    c1.metric("📦 ВСЕГО ККТ", f"{total_kkt} шт")
    
    total_money = df['Итого сумма'].sum()
    c2.metric("💰 КАПИТАЛ", f"{total_money:,.0f} ₽".replace(',', ' '))
    
    total_fn = df['Остатки ФН-15'].sum() + df['Остатки ФН-36'].sum()
    c3.metric("📑 ЗАПАС ФН", f"{int(total_fn)} шт")

    st.divider()

    # --- МОДНАЯ АНАЛИТИКА ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🍩 Доли по складам")
        if total_kkt > 0:
            fig_pie = px.pie(df, values='Остатки ККТ', names='Склад', hole=0.6,
                             color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Нет данных для отображения круга")

    with col_r:
        st.subheader("📊 Наличие в городах")
        if total_kkt > 0:
            # Показываем топ-15 городов
            top_cities = df.nlargest(15, 'Остатки ККТ')
            fig_bar = px.bar(top_cities, x='Склад', y='Остатки ККТ', color='Остатки ККТ', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- ТАБЛИЦА ---
    st.subheader("📋 Детальный реестр (Строки 1-80)")
    search = st.text_input("🔍 Быстрый поиск по названию города или партнера...")
    if search:
        df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    
    st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ Ожидание данных... Проверь, что доступ к Google Таблице открыт для 'Всех, у кого есть ссылка'.")
