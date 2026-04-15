import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="Мониторинг ККТ", layout="wide", page_icon="📊")

# Твоя новая ссылка на таблицу
sheet_id = "1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg"
# Формируем ссылку для прямого скачивания данных
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    # Читаем таблицу, пропуская пустые строки
    df = pd.read_csv(csv_url)
    return df

try:
    df = load_data()
    
    st.sidebar.title("🔐 Авторизация")
    password = st.sidebar.text_input("Введите код доступа", type="password")

    if password == "777":
        st.title("👑 Админ-панель: Учет оборудования")
        
        # --- ФИЛЬТРЫ ---
        st.sidebar.divider()
        st.sidebar.subheader("Фильтры")
        
        # Выбор типа регистрации из колонки A
        if 'Тип рег' in df.columns:
            types = ["Все типы"] + sorted(df['Тип рег'].dropna().unique().tolist())
            selected_type = st.sidebar.selectbox("Тип регистрации:", types)
            
            if selected_type != "Все типы":
                df = df[df['Тип рег'] == selected_type]

        # --- КАРТОЧКИ ---
        col1, col2, col3 = st
