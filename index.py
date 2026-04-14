import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Аналитика ККТ", layout="wide")

st.title("📊 Система учета ФН и ККТ")
st.write("Привет, Дима! Эта панель теперь работает из облака.")

# Блок с твоими показателями
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Отгружено сегодня", "12 шт", "+2")
with col2:
    st.metric("В пути", "45 шт")
with col3:
    st.metric("Зарегистрировано", "85%", "5%")

st.divider()

# Задел под таблицу из Google
st.subheader("📋 Последние отгрузки по регионам")
st.info("Как только подключим таблицу, здесь появится список твоих организаций.")

if st.button('Обновить данные'):
    st.toast('Подключаюсь к Google Таблице...')
