import streamlit as st
import pandas as pd

st.set_page_config(page_title="LOGISTICS: Посылки", layout="wide", page_icon="🚚")
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Читаем данные со 150 строки (пропускаем 149)
df_log = pd.read_csv(URL, skiprows=149).fillna("")

st.title("🚚 Мониторинг отгрузок (со 150 стр.)")
search = st.text_input("🔍 Найти посылку по треку, городу или дате")

if search:
    df_log = df_log[df_log.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

st.dataframe(df_log, use_container_width=True)
