import streamlit as st

st.set_page_config(page_title="Аналитика ККТ", layout="wide")

st.title("📊 Мониторинг отгрузок ФН")

# Блок с ключевыми показателями
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Отгружено (шт)", "150", "+5")
with col2:
    st.metric("Регистраций", "124", "82%")
with col3:
    st.metric("Остаток на складе", "26")

st.divider()

# Заглушка для будущей таблицы
st.subheader("📋 Последние отгрузки организациям")
st.info("Здесь будет список из твоей Google Таблицы")

# Кнопка для проверки
if st.button("Обновить данные"):
    st.toast("Подключаюсь к Google Таблице...")
