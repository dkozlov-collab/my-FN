import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="Мониторинг ФН", layout="wide", page_icon="📊")

# Ссылка на твою таблицу в формате CSV для чтения
sheet_id = "1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg"
gid = "792602024"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=60)  # Данные обновляются раз в минуту
def load_data():
    return pd.read_csv(csv_url)

try:
    df = load_data()
    
    st.sidebar.title("🔐 Доступ")
    password = st.sidebar.text_input("Введите код", type="password")

    if password == "777":
        st.title("👑 Админ-панель: Учет оборудования")
        
        # --- ФИЛЬТР ИЗ ВЫПАДАЮЩЕГО СПИСКА ---
        st.subheader("🔍 Фильтр по типу регистрации")
        
        # Получаем уникальные значения из первой колонки (Тип рег)
        types = ["Все типы"] + sorted(df['Тип рег'].dropna().unique().tolist())
        selected_type = st.selectbox("Выберите статус из колонки 'Тип рег':", types)

        # Фильтруем таблицу
        if selected_type != "Все типы":
            filtered_df = df[df['Тип рег'] == selected_type]
        else:
            filtered_df = df

        # --- СТАТИСТИКА (МЕТРИКИ) ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Найдено строк", len(filtered_df))
        col2.metric("Всего в базе", len(df))
        
        st.divider()

        # --- ОТОБРАЖЕНИЕ ТАБЛИЦЫ ---
        st.write(f"Показываем данные для: {selected_type}")
        st.dataframe(filtered_df, use_container_width=True)

    else:
        st.title("📊 Мониторинг ККТ")
        st.warning("Для просмотра данных введите пароль в боковом меню.")

except Exception as e:
    st.error("Ошибка доступа к данным.")
    st.write("Убедитесь, что в таблице включен доступ 'Все, у кого есть ссылка'.")
    st.write(f"Техническая ошибка: {e}")
