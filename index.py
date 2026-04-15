import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под мобильный Pocophone (светлый дизайн)
st.set_page_config(page_title="RBS: Аналитика склада", layout="wide")

# Стиль: светлый фон, синие акценты
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #212529; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 26px; font-weight: bold; }
    h1, h2, h3 { color: #343A40 !important; font-family: sans-serif; }
    .stDataFrame { border: 1px solid #EEE; }
</style>
""", unsafe_allow_html=True)

# Твоя ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val): return 0
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    """Умный поиск колонки (игнорирует переносы и пробелы)"""
    for c in df.columns:
        if key.lower() in str(c).replace('\n', ' ').lower():
            return c
    return None

@st.cache_data(ttl=10)
def load_stock_data():
    try:
        # Загружаем данные и обрезаем: строки до 80, столбцы A-R (0-17)
        df = pd.read_csv(URL).fillna(0)
        df = df.iloc[:80, :18] 
        return df
    except Exception as e:
        st.error(f"Ошибка доступа к таблице: {e}")
        return pd.DataFrame()

st.title("📊 Аналитика склада RBS")

df = load_stock_data()

if not df.empty:
    # Ищем колонки в диапазоне A:R
    c_sp = find_col(df, 'Партнер')
    c_city = find_col(df, 'Склад')
    c_kkt = find_col(df, 'ККТ')
    c_fn15 = find_col(df, 'ФН-15')
    c_fn36 = find_col(df, 'ФН-36')

    # --- ФИЛЬТРЫ ---
    st.sidebar.header("🎯 Настройки")
    p_list = ["Все партнеры"] + sorted([str(x) for x in df[c_sp].unique() if x != 0 and x != ""]) if c_sp else ["Все"]
    sel_p = st.sidebar.selectbox("Выберите партнера", p_list)

    df_f = df.copy()
    if sel_p != "Все партнеры":
        df_f = df_f[df_f[c_sp].astype(str) == sel_p]

    # --- KPI (ИТОГИ) ---
    m1, m2, m3 = st.columns(3)
    
    # Чистим числа
    if c_kkt: df_f[c_kkt] = df_f[c_kkt].apply(clean_num)
    if c_fn15: df_f[c_fn15] = df_f[c_fn15].apply(clean_num)
    if c_fn36: df_f[c_fn36] = df_f[c_fn36].apply(clean_num)
    
    val_kkt = df_f[c_kkt].sum() if c_kkt else 0
    val_fn = (df_f[c_fn15].sum() if c_fn15 else 0) + (df_f[c_fn36].sum() if c_fn36 else 0)

    m1.metric("📦 ККТ всего", f"{val_kkt} шт")
    m2.metric("📑 ФН (15/36) всего", f"{val_fn} шт")
    m3.metric("📍 Складов", len(df_f[df_f[c_kkt] > 0]))

    st.divider()

    # --- ГРАФИКИ ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("#### Доли по ККТ")
        if val_kkt > 0:
            fig = px.pie(df_f[df_f[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.5)
            fig.update_layout(margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.write("#### Топ-10 складов")
        if val_kkt > 0:
            top_df = df_f.nlargest(10, c_kkt)
            st.bar_chart(top_df.set_index(c_city)[c_kkt])

    # --- ТАБЛИЦА ---
    st.write("#### 📋 Детальные остатки (A-R)")
    st.dataframe(df_f, use_container_width=True, hide_index=True)

else:
    st.info("Проверь доступ к Google Таблице (кнопка 'Поделиться')")
