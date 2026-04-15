import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Установка стиля страницы
st.set_page_config(page_title="ERP 2026: Склады & Логистика", layout="wide", page_icon="🚀")

# Ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(val):
    try:
        if isinstance(val, str):
            val = val.replace(r'[^\d.]', '').replace(',', '.')
        return int(float(val))
    except:
        return 0

@st.cache_data(ttl=20)
def load_data_pro():
    full_df = pd.read_csv(URL).fillna("")
    df_s = full_df.iloc[0:80].copy()
    df_l = full_df.iloc[149:].copy()
    
    num_cols = ['Остатки ККТ', 'Остатки ФН-15', 'Остатки ФН-36', 'Остатки SIM', 'Итого сумма', 'План']
    for col in num_cols:
        if col in df_s.columns:
            df_s[col] = df_s[col].apply(clean_num)
    return df_s, df_l

# --- ИНТЕРФЕЙС ---
st.sidebar.title("💎 Управление 2026")
pwd = st.sidebar.text_input("Введите ключ доступа", type="password")

if pwd == "777":
    df_s, df_l = load_data_pro()
    
    # Заголовок с анимацией (символически)
    st.markdown("# 🚀 Глобальный Мониторинг: Склад + Отгрузки")
    
    # ВЕРХНИЕ КАРТОЧКИ (KPI)
    total_kkt = df_s['Остатки ККТ'].sum()
    total_money = df_s['Итого сумма'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 ОБОРУДОВАНИЕ", f"{total_kkt} шт", "+12% за неделю")
    c2.metric("💰 КАПИТАЛ", f"{total_money:,.0f} ₽".replace(',', ' '))
    c3.metric("🚚 В ОТГРУЗКЕ", f"{len(df_l)} позиций")

    st.divider()

    # ОСНОВНЫЕ ВКЛАДКИ
    tab_dash, tab_stock, tab_logistic = st.tabs(["🔥 Трендовая Аналитика", "📝 База Остатков", "🚛 Логистика 150+"])

    with tab_dash:
        st.subheader("📊 Визуализация потоков данных")
        
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            # Модный Donut Chart
            st.write("### Доли Партнеров (ККТ)")
            fig_pie = px.pie(df_s, values='Остатки ККТ', names='Сервис Партнер', 
                             hole=0.6, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with row1_col2:
            # Индикатор выполнения Плана (Gauge Chart)
            st.write("### Выполнение Плана 2026")
            plan_total = df_s['План'].sum() if 'План' in df_s.columns else 1000
            progress = (total_kkt / plan_total) * 100 if plan_total > 0 else 0
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = progress,
                title = {'text': "Заполнение складов (%)"},
                gauge = {'axis': {'range': [None, 100]},
                         'bar': {'color': "#00ffcc"},
                         'steps' : [
                             {'range': [0, 50], 'color': "lightgray"},
                             {'range': [50, 85], 'color': "gray"}]}))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Нижний график - объемный бар
        st.write("### 🏙️ Остатки по Топ-10 Городам")
        top_cities = df_s.nlargest(10, 'Остатки ККТ')
        fig_bar = px.bar(top_cities, x='Склад', y='Остатки ККТ', color='Остатки ККТ',
                         text_auto='.2s', title="Лидеры по наличию")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab_stock:
        st.subheader("🔍 Поиск и фильтрация массива 1-80")
        search = st.text_input("Введите название города или номер ФН")
        if search:
            df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(df_s, use_container_width=True)
        with tab_logistic:
        st.subheader("🚛 Отгрузки в пути (Массив 150+)")
        st.info("Здесь отображаются все посылки и треки, записанные со 150-й строки")
        # Поиск по логистике
        search_l = st.text_input("Поиск по трек-номеру или получателю")
        if search_l:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
        st.dataframe(df_l, use_container_width=True)
        
        # Кнопка экспорта
        csv = df_l.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Скачать лог отгрузок", csv, "logistics_2026.csv")

else:
    st.title("🛰️ ERP SYSTEM 2026")
    st.warning("Требуется авторизация")
    st.image("https://img.freepik.com/free-vector/abstract-technology-background_23-2148911428.jpg")
