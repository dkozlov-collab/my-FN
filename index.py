import streamlit as st

# Настройка страницы (иконка и широкое отображение)
st.set_page_config(page_title="Мониторинг ФН", layout="wide", page_icon="📊")

# --- БОКОВАЯ ПАНЕЛЬ (ВХОД И РОЛИ) ---
st.sidebar.title("🔐 Доступ к системе")

# Поле для ввода пароля (скрывает символы)
password = st.sidebar.text_input("Введите ваш секретный код", type="password")

# Базовые роли, доступные всем
roles = ["Альфа-Банк", "Менеджеры", "Партнеры"]

# Твой личный доступ (пароль 777)
if password == "777":
    roles.insert(0, "👑 АДМИН (Дима)")
    st.sidebar.success("Привет, Дима! Админка открыта.")
elif password != "":
    st.sidebar.error("Неверный код доступа")

# Выбор раздела
user_role = st.sidebar.radio("Выберите раздел статистики:", roles)

# --- ГЛАВНЫЙ ЭКРАН ---
st.title("📊 Система управления данными ККТ")
st.write(f"Текущий режим: {user_role}")
st.divider()

if user_role == "👑 АДМИН (Дима)":
    st.header("⚙️ Панель управления (Все регионы)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего ФН", "1,250 шт", "+12")
    col2.metric("Активных ККТ", "840 шт", "+5")
    col3.metric("Выручка (день)", "450к ₽", "15%")
    col4.metric("Ошибки ККТ", "2 шт", "-1", delta_color="inverse")
    
    st.subheader("📋 Полный лог операций")
    st.info("Здесь будет твоя полная Google Таблица со всеми данными.")

elif user_role == "Альфа-Банк":
    st.header("🏦 Статистика для Альфа-Банка")
    st.info("Данные по партнерскому коду: 120-46")
    col1, col2 = st.columns(2)
    col1.metric("Регистраций сегодня", "18 шт")
    col2.metric("В обработке", "5 шт")

elif user_role == "Менеджеры":
    st.header("👨‍💻 Рабочий стол менеджера")
    st.write("План по отгрузкам на апрель:")
    st.progress(72) # Шкала на 72%
    st.metric("План выполнен на", "72%", "+3%")

elif user_role == "Партнеры":
    st.header("🤝 Личный кабинет партнера")
    partner_id = st.selectbox("Выберите ваш ID:", ["Ульяновск-01", "Самара-05", "Казань-03"])
    st.write(f"Отображаем данные для: {partner_id}")
    st.warning("Для просмотра детальных отчетов обратитесь к администратору.")
