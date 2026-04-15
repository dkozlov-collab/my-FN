import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ERP 2026: Склад & Логистика", layout="wide", page_icon="🚀")

# Твоя ссылка
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
    try:
        full_df = pd.read_csv(URL).fillna("")
        # Массив 1: Остатки (строки 1-80)
        df_s = full_df.iloc[0:80].copy()
        # Массив 2: Логистика (строки 150+)
        df_l = full_df.iloc[149:].copy()
        
        # Чистим числа только если колонки существуют
        num_cols = ['Остатки ККТ', 'Остатки ФН-15', 'Остатки ФН-36', 'Остатки SIM', 'Итого сумма', 'План']
        for col in num_cols:
            if col in df_s.columns:
                df_s[col] = df_s[col].apply(clean_num)
        return df_s, df_l
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- ЛОГИКА ДОСТУПА ---
st.sidebar.title("💎 Управление 2026")
pwd = st.sidebar.text_input("Введите ключ доступа", type="password")

if pwd == "777":
    df_s, df_l = load_data_pro()
    
    if not df_s.empty:
        st.markdown("# 🚀 Глобальный Мониторинг 2026")
        
        # Безопасный расчет KPI
        t_kkt = df_s['Остатки ККТ'].sum() if 'Остатки ККТ' in df_s.columns else 0
        t_money = df_s['Итого сумма'].sum() if 'Итого сумма' in df_s.columns else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 ОБОРУДОВАНИЕ", f"{t_kkt} шт")
        c2.metric("💰 КАПИТАЛ", f"{t_money:,.0f} ₽".replace(',', ' '))
        c3.metric("🚛 В ОТГРУЗКЕ", f"{len(df_l)} поз.")

        st.divider()

        # ВКЛАДКИ
        tab_dash, tab_stock, tab_logistic = st.tabs(["🔥 Аналитика 2026", "📝 Склад (1-80)", "🚛 Логистика (150+)"])

        with tab_dash:
            st.subheader("📊 Трендовая визуализация")
            col_pie, col_gauge = st.columns(2)
            
            with col_pie:
                if 'Сервис Партнер' in df_s.columns and t_kkt > 0:
                    fig_pie = px.pie(df_s, values='Остатки ККТ', names='Сервис Партнер', hole=0.6)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Нет данных для круговой диаграммы")
                
            with col_gauge:
                plan_val = df_s['План'].sum() if 'План' in df_s.columns and df_s['План'].sum() > 0 else 1000
                progress = min((t_kkt / plan_val) * 100, 100) if plan_val > 0 else 0
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = progress,
                    title = {'text': "Заполнение складов (%)"},
                    gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00ffcc"}}
                ))
                st.plotly_chart(fig_gauge, use_container_width=True)

        with tab_stock:
            st.subheader("🔍 Поиск по складу")
            search_s = st.text_input("Найти город или ФН...")
            df_display = df_s.copy()
            if search_s:
                df_display = df_display[df_display.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
            st.dataframe(df_display, use_container_width=True)

        with tab_logistic:
            st.subheader("🚛 Отгрузки в пути (Массив 150+)")
            search_l = st.text_input("Поиск по треку или посылке...")
            df_l_display = df_l.copy()
            if search_l:
                df_l_display = df_l_display[df_l_display.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
            st.dataframe(df_l_display, use_container_width=True)
    else:
        st.error("Таблица пуста или недоступна.")
else:
    st.title("🛰️ ERP SYSTEM 2026")
    st.info("Введите пароль '777' для входа.")
