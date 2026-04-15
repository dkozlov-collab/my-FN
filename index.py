import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка футуристичного стиля
st.set_page_config(page_title="RBS: ККТ & ФН Мониторинг", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; }
    .stDataFrame { border: 1px solid #444; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    for c in df.columns:
        if key.lower() in c.replace('\n', ' ').lower(): return c
    return None

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL).head(80).fillna(0)
        # Чистим ККТ и ФН сразу во всей таблице
        for col in df.columns:
            if any(x in col.lower() for x in ['ккт', 'фн', 'сумма']):
                df[col] = df[col].apply(clean_num)
        return df
    except: return pd.DataFrame()

# --- ИНТЕРФЕЙС ---
st.markdown("<h1 style='text-align: center;'>📡 МОНИТОРИНГ: ККТ И ФН 2026</h1>", unsafe_allow_html=True)

df_raw = load_data()

if not df_raw.empty:
    # Ищем колонки
    c_sp = find_col(df_raw, 'Партнер')
    c_kkt = find_col(df_raw, 'ККТ')
    c_fn15 = find_col(df_raw, 'ФН-15')
    c_fn36 = find_col(df_raw, 'ФН-36')
    c_city = find_col(df_raw, 'Склад')

    # Фильтр в сайдбаре
    st.sidebar.header("🎯 Фильтр")
    partners = ["ВСЕ"] + sorted([str(p) for p in df_raw[c_sp].unique() if p != 0])
    sel_p = st.sidebar.selectbox("Выберите Банк/Партнера:", partners)

    df_filtered = df_raw.copy()
    if sel_p != "ВСЕ":
        df_filtered = df_filtered[df_filtered[c_sp] == sel_p]

    # --- КРУПНЫЕ ПОКАЗАТЕЛИ ---
    m1, m2, m3 = st.columns(3)
    
    total_kkt = df_filtered[c_kkt].sum() if c_kkt else 0
    total_fn15 = df_filtered[c_fn15].sum() if c_fn15 else 0
    total_fn36 = df_filtered[c_fn36].sum() if c_fn36 else 0
    
    m1.metric("📦 ККТ ВСЕГО", f"{total_kkt} шт")
    m2.metric("📑 ФН-15", f"{total_fn15} шт")
    m3.metric("📑 ФН-36", f"{total_fn36} шт")

    st.divider()

    # --- ГРАФИКИ (Дизайн как ты хотел) ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### 🍩 Распределение ККТ")
        if total_kkt > 0:
            fig = px.pie(df_filtered[df_filtered[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.6)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
    with col_r:
        st.write("### 📊 Запасы ФН по городам")
        if c_city:
            # Складываем оба ФН для графика
            df_filtered['Всего ФН'] = df_filtered[c_fn15] + df_filtered[c_fn36]
            fig_bar = px.bar(df_filtered[df_filtered['Всего ФН']>0], x=c_city, y='Всего ФН', color='Всего ФН', text_auto=True)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- ТАБЛИЦА ---
    st.write("### 📋 Полный реестр (ККТ и ФН)")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

else:
    st.error("Ошибка доступа! Проверь кнопку 'Поделиться' в таблице.")
