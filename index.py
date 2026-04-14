import streamlit as st
import pandas as pd

st.set_page_config(page_title="Админка ККТ", layout="wide")

st.title("📊 Система учета ФН и ККТ")

# Тестовая панель
st.write("Привет, Дима! Твой сайт теперь работает из облака.")

col1, col2, col3 = st.columns(3)
col1.metric("Отгружено сегодня", "12 шт", "+2")
col2.metric("В пути", "45 шт")
col3.metric("Зарегистрировано", "85%", "5%")

st.info("Следующим шагом мы подключим сюда твою Google Таблицу!")
