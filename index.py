import streamlit as st
import pandas as pd

# Настройка широкого экрана (Excel-style)
st.set_page_config(page_title="RBS: Логистика 1150+", layout="wide", page_icon="🚚")

# Ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=15)
def load_logistics_1150():
    try:
        # Читаем всю таблицу
        full_df = pd.read_csv(URL).fillna("")
        
        # Забираем данные начиная со строки 1150 (в Python индекс 1149)
        if len(full_df) >= 1150:
            df_logic = full_df.iloc[1149:].copy()
            # Убираем пустые строки, чтобы не мусорить
            df_logic = df_logic[df_logic.astype(str).apply(lambda x: x.str.strip()).ne("").any(axis=1)]
            return df_logic
        else:
            return pd.DataFrame(columns=["Статус"], data=[["Строка 1150 еще не заполнена"]])
    except Exception as e:
        st.error(f"Ошибка чтения таблицы: {e}")
        return pd.DataFrame()

# ЗАГОЛОВОК
st.markdown("<h2 style='color: #00E5FF;'>🚚 РЕЕСТР ЛОГИСТИКИ (Строки 1150+)</h2>", unsafe_allow_html=True)

df = load_logistics_1150()

if not df.empty:
    # Поиск прямо над таблицей
    search = st.text_input("🔍 Быстрый поиск по серийнику, городу или статусу 'В ПУТИ'...")
    
    if search:
        # Фильтруем по всем колонкам
        mask = df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    # ВЫВОД В ВИДЕ ТАБЛИЦЫ (Excel-вид)
    # Используем st.dataframe — это самый компактный вид
    st.dataframe(
        df, 
        use_container_width=True, 
        height=800, # Делаем таблицу высокой, чтобы видеть много строк
        hide_index=True
    )
    
    st.caption(f"Показано строк из раздела логистики: {len(df)}")

else:
    st.warning("Данные на строке 1150 и ниже не найдены. Проверь таблицу!")
