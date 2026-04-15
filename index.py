import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка широкого экрана
st.set_page_config(page_title="ERP: Склады ККТ", layout="wide", page_icon="📈")

# Ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=30) # Данные обновляются каждые 30 секунд
def load_massive_data():
    df = pd.read_csv(URL).fillna(0)
    # Массовое преобразование колонок в числа
    cols = ['Остатки ККТ', 'Мин. остаток', 'В пути ККТ', 'План']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

# --- ЛОГИКА ДОСТУПА ---
st.sidebar.title("🛠️ Управление")
pwd = st.sidebar.text_input("Пароль доступа", type="password")

if pwd == "777":
    df = load_massive_data()
    
    # --- ГЛОБАЛЬНЫЙ ПОИСК ---
    st.title("🚀 Массивный мониторинг оборудования")
    search_query = st.text_input("🔍 Глобальный поиск (введите город, партнера или тип рег.)", "")

    # Фильтрация по поиску
    if search_query:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df = df[mask]

    # --- KPI ПАНЕЛЬ (ГЛАВНЫЕ ЦИФРЫ) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Всего ККТ", f"{df['Остатки ККТ'].sum()} шт")
    
    transit_sum = df['В пути ККТ'].sum() if 'В пути ККТ' in df.columns else 0
    c2.metric("🚚 В пути", f"{transit_sum} шт")
    
    low_stock = df[df['Остатки ККТ'] < df['Мин. остаток']].shape[0]
    c3.metric("⚠️ Дефицит", f"{low_stock} складов", delta_color="inverse")
    
    c4.metric("🏙️ Активных локаций", df['Склад'].nunique())

    st.divider()

    # --- ВКЛАДКИ ---
    tab_stat, tab_table, tab_alert = st.tabs(["📊 Объемная Аналитика", "📝 Реестр данных", "🚨 Критические остатки"])

    with tab_stat:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.write("### Доля рынка партнеров")
            fig_pie = px.pie(df, values='Остатки ККТ', names='Сервис Партнер', hole=0.5,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_right:
            st.write("### Топ складов по наличию")
            top_cities = df.groupby('Склад')['Остатки ККТ'].sum().nlargest(10).reset_index()
            fig_bar = px.bar(top_cities, x='Остатки ККТ', y='Склад', orientation='h', 
                             color='Остатки ККТ', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_table:
        st.write("### Полный массив данных")
        # Добавляем возможность сортировки и поиска прямо в таблице
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Выгрузить массив в CSV", csv, "full_export.csv", "text/csv")

    with tab_alert:
        st.write("### 🚨 Склады, требующие отгрузки")
        # Показываем только те, где остаток меньше минимального
        alert_df = df[df['Остатки ККТ'] < df['Мин. остаток']]
        if not alert_df.empty:
            st.warning(f"Найдено {len(alert_df)} проблемных зон!")
            st.table(alert_df[['Склад', 'Сервис Партнер', 'Остатки ККТ', 'Мин. остаток']])
        else:
            st.success("Все склады укомплектованы согласно нормативам!")

else:
    st.title("🏗️ Мониторинг Складов")
    st.info("Введите пароль '777' для активации движка.")
