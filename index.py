import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка стиля 2026
st.set_page_config(page_title="RBS: Склад 1-80", layout="wide", page_icon="🏢")

# Ссылка на таблицу (первая база)
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except:
        return 0

@st.cache_data(ttl=15)
def load_stock_only():
    try:
        # Читаем СТРОГО до 80 строки
        df = pd.read_csv(URL).head(80).fillna(0)
        
        # Чистим данные для графиков
        num_cols = ['Остатки ККТ', 'Итого сумма', 'Остатки ФН-15', 'Остатки ФН-36']
        for col in num_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_num)
        return df
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return pd.DataFrame()

# ЗАГОЛОВОК
st.markdown("<h1 style='text-align: center; color: #00E5FF;'>🏢 МОНИТОРИНГ СКЛАДОВ (1-80)</h1>", unsafe_allow_html=True)

df = load_stock_only()

if not df.empty:
    # --- БОКОВАЯ ПАНЕЛЬ (ФИЛЬТРЫ) ---
    st.sidebar.header("🎯 Фильтр Партнеров")
    if 'Сервис Партнер' in df.columns:
        # Убираем нули и пустые из списка партнеров
        partners = ["ВСЕ"] + sorted([str(p) for p in df['Сервис Партнер'].unique() if p != 0 and p != "0"])
        sel_p = st.sidebar.selectbox("Выберите банк/партнера:", partners)
        
        if sel_p != "ВСЕ":
            df = df[df['Сервис Партнер'] == sel_p]

    # --- KPI БЛОК ---
    c1, c2, c3 = st.columns(3)
    total_kkt = int(df['Остатки ККТ'].sum())
    c1.metric("📦 ККТ В НАЛИЧИИ", f"{total_kkt} шт")
    
    total_money = df['Итого сумма'].sum()
    c2.metric("💰 СУММА ЗАПАСОВ", f"{total_money:,.0f} ₽".replace(',', ' '))
    
    total_fn = int(df['Остатки ФН-15'].sum() + df['Остатки ФН-36'].sum())
    c3.metric("📑 ВСЕГО ФН", f"{total_fn} шт")

    st.divider()

    # --- ГРАФИКИ (ПЕРЧИНКА 2026) ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### 🍩 Доли по Складам")
        if total_kkt > 0:
            fig = px.pie(df[df['Остатки ККТ']>0], values='Остатки ККТ', names='Склад', hole=0.6)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")

    with col_r:
        st.write("### 📈 Топ Городов")
        if total_kkt > 0:
            # Берем топ-10 по остаткам
            top_10 = df.nlargest(10, 'Остатки ККТ')
            fig_bar = px.bar(top_10, x='Склад', y='Остатки ККТ', color='Остатки ККТ', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- ТАБЛИЦА (EXCEL ВИД) ---
    st.write("### 📋 Детальный реестр (Строки 1-80)")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("Проверь доступ к таблице!")
