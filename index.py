import streamlit as st
import pandas as pd

st.set_page_config(page_title="Мониторинг Складов", layout="wide")

# Твой ID таблицы
ID = "1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg"
URL = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv"

st.sidebar.title("🔐 Авторизация")
pwd = st.sidebar.text_input("Пароль", type="password")

if pwd == "777":
    try:
        # Читаем данные через Google Visualization API (самый мощный способ)
        df = pd.read_csv(URL)
        
        # Убираем пустые столбцы, если они есть
        df = df.dropna(axis=1, how='all')

        st.title("👑 Админ-панель: Учет ККТ")
        
        # Статистика сверху
        col1, col2 = st.columns(2)
        if 'Остатки ККТ' in df.columns:
            col1.metric("Всего ККТ", int(df['Остатки ККТ'].sum()))
        if 'Склад' in df.columns:
            col2.metric("Кол-во Складов", df['Склад'].nunique())

        st.divider()

        # График
        if 'Склад' in df.columns and 'Остатки ККТ' in df.columns:
            st.subheader("📊 Остатки по городам")
            st.bar_chart(df.set_index('Склад')['Остатки ККТ'])

        # Сама таблица
        st.subheader("📋 Детальный отчет")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка доступа. Google всё еще блокирует запрос.")
        st.info("Дима, проверь: Файл -> Поделиться -> Опубликовать в интернете -> Опубликовать.")
else:
    st.title("🛡️ Система мониторинга")
    st.write("Введите код доступа в боковом меню.")
