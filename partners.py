import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы 2026
st.set_page_config(page_title="RBS: Регистрация", layout="wide", page_icon="💎")

# Ссылка на твою таблицу
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def clean_num(val):
    try:
        if isinstance(val, str):
            val = val.replace(r'[^\d.]', '').replace(',', '.')
        return int(float(val))
    except:
        return 0

@st.cache_data(ttl=20)
def load_data():
    # Работаем строго с массивом регистрации (строки 1-80)
    df = pd.read_csv(URL).head(80).fillna(0)
    # Колонки для аналитики
    num_cols = ['Остатки ККТ', 'Остатки ФН-15', 'Остатки ФН-36', 'Остатки SIM', 'Итого сумма', 'План']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)
    return df

# --- ДИЗАЙН ИНТЕРФЕЙСА ---
st.markdown("<h1 style='text-align: center; color: #00E5FF;'>💎 ПОРТАЛ РЕГИСТРАЦИИ RBS 2026</h1>", unsafe_allow_html=True)

df = load_data()

# --- ФИЛЬТРЫ В БОКОВОЙ ПАНЕЛИ ---
st.sidebar.title("⚙️ Настройки")
if 'Сервис Партнер' in df.columns:
    partner_list = ["ВСЕ ПАРТНЕРЫ"] + sorted(df['Сервис Партнер'].unique().tolist())
    selected_p = st.sidebar.selectbox("🎯 Выберите партнера/банк:", partner_list)
    
    if selected_p != "ВСЕ ПАРТНЕРЫ":
        df = df[df['Сервис Партнер'] == selected_p]

# --- KPI СЕКЦИЯ ---
c1, c2, c3, c4 = st.columns(4)
total_kkt = int(df['Остатки ККТ'].sum())
total_money = df['Итого сумма'].sum()
total_sim = int(df['Остатки SIM'].sum() if 'Остатки SIM' in df else 0)

c1.metric("📦 ККТ В НАЛИЧИИ", f"{total_kkt} шт")
c2.metric("💰 КАПИТАЛ", f"{total_money:,.0f} ₽".replace(',', ' '))
c3.metric("📱 SIM-КАРТЫ", f"{total_sim} шт")
c4.metric("🏙️ ГОРОДОВ", len(df['Склад'].unique()))

st.divider()

# --- ТРЕНДОВАЯ АНАЛИТИКА (ГРАФИКИ) ---
t_col1, t_col2 = st.columns(2)

with t_col1:
    st.write(f"### 🍩 Доли регистрации: {selected_p}")
    # Модный пончиковый график
    fig_donut = px.pie(df, values='Остатки ККТ', names='Склад', hole=0.6,
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_donut.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

with t_col2:
    st.write("### 📈 Динамика по складам")
    # Объемный график
    fig_bar = px.bar(df.nlargest(15, 'Остатки ККТ'), x='Склад', y='Остатки ККТ', 
                     color='Остатки ККТ', text_auto=True,
                     color_continuous_scale='Teal')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- ДЕТАЛЬНЫЙ РЕЕСТР ---
st.divider()
st.subheader("📋 Детальный реестр регистраций")
search = st.text_input("🔍 Быстрый поиск (город, серийник, партнер)...")
if search:
    df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)

# Кнопка экспорта
st.sidebar.divider()
csv = df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 Скачать этот отчет", csv, "rbs_registration.csv")
