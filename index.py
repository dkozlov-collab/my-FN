import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ADMIN: Склады ККТ", layout="wide", page_icon="👑")

URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=20)
def load_stock():
    df = pd.read_csv(URL).head(80).fillna(0)
    # Чистим только те колонки, что есть в этом блоке
    for c in ['Остатки ККТ', 'Итого сумма', 'План']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    return df

st.sidebar.title("🔐 Доступ")
if st.sidebar.text_input("Пароль", type="password") == "777":
    df = load_stock()
    st.title("👑 Глобальный мониторинг Остатков")
    
    # Модные KPI
    total_kkt = df['Остатки ККТ'].sum() if 'Остатки ККТ' in df.columns else 0
    st.metric("📦 ВСЕГО ККТ НА СКЛАДАХ", f"{int(total_kkt)} шт")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Доли Партнеров")
        fig = px.pie(df, values='Остатки ККТ', names='Сервис Партнер', hole=0.6)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write("### Топ городов")
        st.bar_chart(df.set_index('Склад')['Остатки ККТ'].nlargest(10))
    
    st.dataframe(df, use_container_width=True)
