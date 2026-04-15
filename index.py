mport streamlit as st

st.set_page_config(page_title="Мониторинг ФН", layout="wide")

st.title("📊 Система учета ФН и ККТ")
st.write("Привет, Дима! Эта панель обновляется из GitHub.")

# Твои показатели
col1, col2, col3 = st.columns(3)
col1.metric("Отгружено сегодня", "15 шт", "+3")
col2.metric("В пути", "38 шт")
col3.metric("Зарегистрировано", "88%", "2%")

st.divider()

st.info("💡 Следующим шагом мы выведем сюда данные из твоей Google Таблицы.")
