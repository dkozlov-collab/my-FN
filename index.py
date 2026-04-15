import streamlit as st
import pandas as pd
import plotly.express as px # Для красивых круглых диаграмм

st.set_page_config(page_title="Учет ККТ: Склады СП", layout="wide", page_icon="🏗️")

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

# Функция для безопасного превращения в числа
def clean_num(val):
    try:
        return int(float(str(val).replace(',', '.').strip()))
    except:
        return 0

@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url).fillna(0)
    # Чистим числа
    num_cols = ['Остатки ККТ', 'Мин. остаток', 'В пути ККТ']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)
    return df

# --- ЛОГИКА ВХОДА ---
st.sidebar.title("🔐 Кабинет")
pwd = st.sidebar.text_input("Код доступа", type="password")

if pwd == "777":
    try:
        df = load_data(URL)
        
        st.title("🏗️ Мониторинг Складов (Админ)")

        # --- ВКЛАДКИ (РАЗДЕЛЬНО) ---
        t1, t2, t3, t4, t5 = st.tabs(["📊 Аналитика (Круглые)", "🤝 Партнеры", "🚚 В пути / Отгрузки", "🛰️ Удаленка", "📋 База / Наталья (АБ)"])

        with t1:
            st.subheader("📊 Распределение ККТ (Всего)")
            
            # Круговая диаграмма: ККТ по партнерам
            if 'Сервис Партнер' in df.columns and 'Остатки ККТ' in df.columns:
                pie_data = df.groupby('Сервис Партнер')['Остатки ККТ'].sum().reset_index()
                fig_pie = px.pie(pie_data, values='Остатки ККТ', names='Сервис Партнер', title='ККТ по Сервис-Партнерам')
                st.plotly_chart(fig_pie, use_container_width=True)

            # Гистограмма: Динамика по городам
            if 'Склад' in df.columns and 'Остатки ККТ' in df.columns:
                st.write("📈 Динамика остатков по городам")
                city_data = df.groupby('Склад')['Остатки ККТ'].sum().sort_values(ascending=False).reset_index()
                fig_bar = px.bar(city_data, x='Склад', y='Остатки ККТ', title='ККТ по городам')
                st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.subheader("Фильтр по партнерам")
            partner = st.selectbox("Выберите партнера:", sorted(df['Сервис Партнер'].unique()))
            p_df = df[df['Сервис Партнер'] == partner]
            
            # Круговая диаграмма для партнера (ККТ по городам)
            if 'Склад' in p_df.columns:
                p_pie_data = p_df.groupby('Склад')['Остатки ККТ'].sum().reset_index()
                fig_p_pie = px.pie(p_pie_data, values='Остатки ККТ', names='Склад', title=f'ККТ у {partner} по городам')
                st.plotly_chart(fig_p_pie, use_container_width=True)
                
            st.metric(f"Всего ККТ у {partner}", f"{p_df['Остатки ККТ'].sum()} шт")
            st.dataframe(p_df, use_container_width=True)

        with t3:
            st.subheader("🚚 Мониторинг отгрузок в пути")
            if 'В пути ККТ' in df.columns:
                in_transit = df[df['В пути ККТ'] > 0]
                st.metric("Сейчас в пути (всего)", f"{in_transit['В пути ККТ'].sum()} шт")
                st.write("Маршруты в пути:")
                st.table(in_transit[['Склад', 'В пути ККТ', 'Сервис Партнер']])
            else:
                st.info("Добавьте колонку 'В пути ККТ' в таблицу")

        with t4:
            st.subheader("🛰️ Удаленные регистрации")
            # Фильтруем строки, где в типе рег есть слово "Уд" или "Удален"
            remote_df = df[df['Тип рег'].str.contains('Уд', na=False)]
            st.metric("Кол-во удаленок", len(remote_df))
            st.dataframe(remote_df, use_container_width=True)

        with t5:
            st.subheader("📋 Полная техническая база")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Скачать CSV", df.to_csv(index=False).encode('utf-8-sig'), "base.csv")
            
            # Вкладка Натальи (Альфа-Банк)
            st.divider()
            st.subheader("👨‍💻 Кабинет Натальи (Альфа-Банк)")
            # Показываем только данные для 'АБ'
            alfa_df = df[df['Сервис Партнер'] == 'АБ']
            if len(alfa_df) > 0:
                col1, col2 = st.columns(2)
                col1.metric("ККТ на складах АБ", f"{alfa_df['Остатки ККТ'].sum()} шт")
                col2.metric("Городов с ККТ АБ", alfa_df['Склад'].nunique())
                st.dataframe(alfa_df, use_container_width=True)
            else:
                st.info("В таблице нет данных для партнера 'АБ'")

    except Exception as e:
        st.error(f"Ошибка: {e}")
else:
    st.title("🏢 Мониторинг ККТ")
    st.info("Введите пароль слева.")
