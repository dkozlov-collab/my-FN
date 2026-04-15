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
    full_df = pd.read_csv(URL).fillna("")
    df_s = full_df.iloc[0:80].copy()
    df_l = full_df.iloc[149:].copy() # Логистика со 150 строки
    
    num_cols = ['Остатки ККТ', 'Остатки ФН-15', 'Остатки ФН-36', 'Остатки SIM', 'Итого сумма', 'План']
    for col in num_cols:
        if col in df_s.columns:
            df_s[col] = df_s[col].apply(clean_num)
    return df_s, df_l

# --- ЛОГИКА ДОСТУПА ---
st.sidebar.title("💎 Управление 2026")
pwd = st.sidebar.text_input("Введите ключ доступа", type="password")

if pwd == "777":
    df_s, df_l = load_data_pro()
    
    st.markdown("# 🚀 Глобальный Мониторинг 2026")
    
    # KPI ПАНЕЛЬ
    t_kkt = df_s['Остатки ККТ'].sum()
    t_money = df_s['Итого сумма'].sum()
    
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
            st.write("### Доли Партнеров (ККТ)")
            fig_pie = px.pie(df_s, values='Остатки ККТ', names='Сервис Партнер', hole=0.6)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_gauge:
            st.write("### Заполнение складов")
            # Считаем процент выполнения плана
            plan_val = df_s['План'].sum() if 'План' in df_s.columns and df_s['План'].sum() > 0 else 1000
            progress = min((t_kkt / plan_val) * 100, 100)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = progress,
                gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00ffcc"}}
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

    with tab_stock:
        st.subheader("🔍 Поиск по складу")
        search_s = st.text_input("Найти город или ФН...")
        if search_s:
            df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
        st.dataframe(df_s, use_container_width=True)

    with tab_logistic:
        st.subheader("🚛 Отгрузки в пути (Массив 150+)")
        search_l = st.text_input("Поиск по треку или посылке...")
        if search_l:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
        st.dataframe(df_l, use_container_width=True)

else:
    st.info("Введите пароль '777' для входа в систему.")
