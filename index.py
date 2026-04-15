import streamlit as st
import pandas as pd

# Настройка широкого экрана
st.set_page_config(page_title="RBS: Логистика Excel-вид", layout="wide", page_icon="🚚")

# Ссылка на твою вторую таблицу
URL_LOGIC = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=10)
def load_logistics():
    try:
        # Читаем данные, пропуская всё до нужной нам части (150 строка)
        df_all = pd.read_csv(URL_LOGIC).fillna("")
        if len(df_all) > 149:
            # Забираем данные со 150 строки и до конца
            df = df_all.iloc[149:].copy()
            # Убираем полностью пустые строки
            df = df[df.astype(str).apply(lambda x: x.str.strip()).ne("").any(axis=1)]
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return pd.DataFrame()

# Заголовок
st.markdown("<h2 style='color: #00E5FF;'>🚚 РЕЕСТР ОТГРУЗОК (Вид: Таблица Excel)</h2>", unsafe_allow_html=True)

df_log = load_logistics()

if not df_log.empty:
    # Панель поиска сверху
    search_query = st.text_input("🔍 Быстрый фильтр по серийным номерам или городам:", placeholder="Введите номер или город...")
    
    if search_query:
        # Фильтрация по всем колонкам одновременно
        df_log = df_log[df_log.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # Вывод данных в виде компактной таблицы
    # Используем st.dataframe для "Excel-вида" с возможностью сортировки
    st.dataframe(
        df_log, 
        use_container_width=True, 
        height=600, # Высота окна с данными
        hide_index=True # Скрываем технические номера строк Python
    )
    
    # Счетчик для контроля
    st.caption(f"Найдено записей: {len(df_log)}")

else:
    st.warning("На 150-й строке данных не обнаружено. Проверь таблицу!")
    st.info("Убедись, что доступ к таблице открыт: 'Все, у кого есть ссылка'.")
