import streamlit as st
import pandas as pd

st.set_page_config(page_title="Мониторинг ККТ", layout="wide")

# Твоя проверенная ссылка
sheet_id = "1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

st.sidebar.title("🔐 Вход")
password = st.sidebar.text_input("Введите пароль", type="password")

if password == "777":
    try:
        # Пытаемся прочитать данные
        df = pd.read_csv(csv_url)
        st.title("👑 Админ-панель: Ульяновск и регионы")
        
        # Фильтр
        if 'Тип рег' in df.columns:
            st.sidebar.divider()
            status = st.sidebar.selectbox("Фильтр:", ["Все"] + list(df['Тип рег'].unique()))
            if status != "Все":
                df = df[df['Тип рег'] == status]

        st.metric("Записей в таблице", len(df))
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error("Ошибка 401: Google не дает доступ.")
        st.info("Дима, проверь в таблице: Поделиться -> Общий доступ -> Все, у кого есть ссылка (Читатель).")
else:
    st.title("📊 Мониторинг")
    st.write("Введите пароль '777' в меню слева")
