import streamlit as st

st.set_page_config(page_title="Аналитика ККТ", layout="wide")

st.title("📊 Мониторинг отгрузок и ФН")
st.write(f"Привет, Дима! Твоя панель управления готова.")

# Карточки с реальными цифрами (пока заглушки)
col1, col2, col3 = st.columns(3)
col1.metric("Отгружено сегодня", "12 шт", "+2")
col2.metric("В пути", "45 шт")
col3.metric("Зарегистрировано", "85%", "5%")

st.divider()

st.subheader("📍 Аналитика по организациям")
st.info("Здесь будет список из твоей Google Таблицы")

# Кнопка обновления
if st.button('Обновить данные из таблицы'):
    st.success('Связь с Google Таблицей установлена!')
