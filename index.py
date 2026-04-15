import streamlit as st
import pandas as pd

st.set_page_config(page_title="Мониторинг ККТ/ФН", layout="wide")

# Ссылка на твою опубликованную таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

# --- ЛОГИКА ВХОДА ---
st.sidebar.title("🔐 Вход в систему")
pwd = st.sidebar.text_input("Пароль", type="password")

# Назначаем права доступа по паролю
if pwd == "777":
    user_role = "Админ"
elif pwd == "111":
    user_role = "Менеджер"
elif pwd == "222":
    user_role = "Альфа-Банк"
elif pwd == "333":
    user_role = "Почта-Банк"
else:
    user_role = None

if user_role:
    try:
        df = pd.read_csv(URL)
        st.title(f"📊 Кабинет: {user_role}")
        
        # --- ФИЛЬТРАЦИЯ ДАННЫХ ---
        if user_role == "Альфа-Банк":
            display_df = df[df['Сервис Партнер'] == 'АБ']
        elif user_role == "Почта-Банк":
            display_df = df[df['Сервис Партнер'] == 'ПБ'] # Убедись, что в таблице так написано
        else:
            display_df = df # Админ и Менеджер видят всё

        # --- БЛОК ГРАФИКОВ (Только для Админа и Менеджера) ---
        if user_role in ["Админ", "Менеджер"]:
            st.subheader("📈 Визуализация остатков")
            # График: Остатки ККТ по городам
            chart_data = display_df.set_index('Склад')['Остатки ККТ']
            st.bar_chart(chart_data)

        # --- СТАТИСТИКА ОТГРУЗОК ---
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        total_kkt = display_df['Остатки ККТ'].sum()
        low_stock = display_df[display_df['Остатки ККТ'] < display_df['Мин. остаток']].shape[0]
        
        col1.metric("Всего ККТ на складах", f"{total_kkt} шт")
        col2.metric("Склады в дефиците", f"{low_stock} шт", delta_color="inverse")
        col3.metric("Активных точек", display_df['Склад'].nunique())

        # --- ТАБЛИЦА ---
        st.subheader("📝 Детальная информация")
        st.dataframe(display_df, use_container_width=True)
        
        # Кнопка скачивания
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Скачать таблицу (Excel/CSV)", csv, "report.csv", "text/csv")

    except Exception as e:
        st.error(f"Ошибка данных: {e}")
else:
    st.title("🛡️ Система мониторинга")
    st.info("Введите пароль:\n\n- 777 (Админ)\n- 111 (Менеджер)\n- 222 (Альфа)\n- 333 (Почта)")
