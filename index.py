import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Мониторинг Складов СП", layout="wide", page_icon="🏢")

# Ссылка на твою таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL).fillna(0)
    # Превращаем в числа для графиков
    cols_to_fix = ['Остатки ККТ', 'Мин. остаток', 'В пути ККТ', 'План']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# --- ЛОГИКА ВХОДА ---
st.sidebar.title("🔐 Личный кабинет")
pwd = st.sidebar.text_input("Введите код", type="password")

if pwd == "777":
    df = load_data()
    
    # --- МОЩНЫЕ ФИЛЬТРЫ СЛЕВА ---
    st.sidebar.header("🔍 Настройки поиска")
    
    # Поиск по партнеру
    all_partners = ["Все партнеры"] + list(df['Сервис Партнер'].unique())
    sel_partner = st.sidebar.selectbox("Выберите партнера (АБ, ПБ и т.д.):", all_partners)
    
    # Поиск по городу
    all_cities = ["Все города"] + sorted(list(df['Склад'].unique()))
    sel_city = st.sidebar.selectbox("Выберите город:", all_cities)

    # Фильтруем базу
    filtered_df = df.copy()
    if sel_partner != "Все партнеры":
        filtered_df = filtered_df[filtered_df['Сервис Партнер'] == sel_partner]
    if sel_city != "Все города":
        filtered_df = filtered_df[filtered_df['Склад'] == sel_city]

    st.title(f"🏢 Пульт: {sel_partner if sel_partner != 'Все партнеры' else 'Все склады'}")

    # --- ВКЛАДКИ ---
    tab_graph, tab_stock, tab_transit = st.tabs(["📊 Красивая аналитика", "📦 Остатки и Планы", "🚚 Отгрузки в пути"])

    with tab_graph:
        st.subheader("Распределение оборудования")
        col1, col2 = st.columns(2)
        
        with col1:
            # Круговая диаграмма - Доли партнеров/городов
            fig_pie = px.pie(filtered_df, values='Остатки ККТ', names='Склад' if sel_partner != "Все партнеры" else 'Сервис Партнер', 
                             hole=0.4, title="Доля остатков (в %)")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            # Динамика: Факт против Плана
            if 'План' in filtered_df.columns:
                fig_bar = px.bar(filtered_df, x='Склад', y=['Остатки ККТ', 'План'], 
                                 barmode='group', title="Факт vs План")
                st.plotly_chart(fig_bar, use_container_width=True)

    with tab_stock:
        st.subheader("📦 Детальный отчет по остаткам")
        
        # Индикаторы дефицита
        def_df = filtered_df[filtered_df['Остатки ККТ'] < filtered_df['Мин. остаток']]
        if not def_df.empty:
            st.error(f"⚠️ Внимание! На {len(def_df)} складах остатки ниже критического уровня!")
        
        st.dataframe(filtered_df[['Склад', 'Сервис Партнер', 'Остатки ККТ', 'Мин. остаток', 'План']], 
                     use_container_width=True)

    with tab_transit:
        st.subheader("🚚 Мониторинг логистики")
        if 'В пути ККТ' in filtered_df.columns:
            transit_df = filtered_df[filtered_df['В пути ККТ'] > 0]
            st.metric("Всего едет к нам", f"{int(transit_df['В пути ККТ'].sum())} шт")
            st.write("Куда ожидаем поставку:")
            st.table(transit_df[['Склад', 'В пути ККТ', 'Сервис Партнер']])
        else:
            st.warning("В таблице нет колонки 'В пути ККТ'")

    # Кнопка скачать
    st.sidebar.divider()
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 Скачать этот отчет", csv, "report.csv", "text/csv")

else:
    st.title("🏗️ Мониторинг Складов")
    st.info("Введите пароль '777' в левом меню")
