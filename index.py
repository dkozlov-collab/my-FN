import streamlit as st
import pandas as pd

st.set_page_config(page_title="Учет ККТ: Склады СП", layout="wide", page_icon="🏢")

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

# --- ЛОГИКА ВХОДА ---
st.sidebar.title("🔐 Личный кабинет")
pwd = st.sidebar.text_input("Введите ваш код", type="password")

if pwd == "777":
    try:
        df = pd.read_csv(URL)
        # Чистим данные от пустых колонок
        df = df.dropna(axis=1, how='all')
        
        st.title("👑 Панель управления Складами")
        
        # --- ФИЛЬТРЫ В БОКОВОЙ ПАНЕЛИ ---
        st.sidebar.divider()
        st.sidebar.subheader("⚙️ Фильтрация")
        
        all_partners = ["Все"] + sorted(df['Сервис Партнер'].dropna().unique().tolist())
        selected_partner = st.sidebar.selectbox("Партнер:", all_partners)
        
        all_cities = ["Все города"] + sorted(df['Склад'].dropna().unique().tolist())
        selected_city = st.sidebar.selectbox("Город/Склад:", all_cities)

        # Применяем фильтры
        filtered_df = df.copy()
        if selected_partner != "Все":
            filtered_df = filtered_df[filtered_df['Сервис Партнер'] == selected_partner]
        if selected_city != "Все города":
            filtered_df = filtered_df[filtered_df['Склад'] == selected_city]

        # --- ВКЛАДКИ ---
        tab1, tab2, tab3 = st.tabs(["📊 Аналитика", "📦 Остатки ККТ", "📋 Весь отчет"])

        with tab1:
            st.subheader(f"Статистика: {selected_partner} / {selected_city}")
            c1, c2, c3 = st.columns(3)
            
            total = int(filtered_df['Остатки ККТ'].sum())
            c1.metric("Всего ККТ", f"{total} шт")
            c2.metric("Складов", filtered_df['Склад'].nunique())
            
            # Считаем дефицит (где остатки < мин)
            if 'Мин. остаток' in filtered_df.columns:
                deficiency = filtered_df[filtered_df['Остатки ККТ'] < filtered_df['Мин. остаток']].shape[0]
                c3.metric("Критические остатки", f"{deficiency} складов", delta="-внимание", delta_color="inverse")

            st.divider()
            st.write("📈 Распределение оборудования по складам")
            # Группируем для красоты графика
            chart_data = filtered_df.groupby('Склад')['Остатки ККТ'].sum().sort_values(ascending=False)
            st.bar_chart(chart_data)

        with tab2:
            st.subheader("📦 Проверка запасов")
            # Показываем только важные для остатков колонки
            stock_cols = ['Склад', 'Тип рег', 'Остатки ККТ', 'Мин. остаток', 'Сервис Партнер']
            st.dataframe(filtered_df[stock_cols], use_container_width=True)
            
            # Кнопка быстрой выгрузки остатков
            csv_stock = filtered_df[stock_cols].to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Скачать список остатков", csv_stock, "ostakti.csv")

        with tab3:
            st.subheader("📝 Полная база данных")
            st.dataframe(filtered_df, use_container_width=True)
            
            csv_full = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Скачать полный отчет (CSV)", csv_full, "full_report.csv")

    except Exception as e:
        st.error(f"Ошибка чтения таблицы. Проверь доступ. ({e})")
else:
    # Главный экран до входа
    st.title("🏢 Система мониторинга ККТ")
    st.info("Пожалуйста, введите ваш секретный код в левом меню для входа в кабинет.")
    st.image("https://img.freepik.com/free-vector/data-report-concept-illustration_114360-883.jpg", width=400)
