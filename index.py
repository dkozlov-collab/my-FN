import streamlit as st
import pandas as pd
import plotly.express as px

# Масштабный интерфейс для Pocophone (Белый, чистый, мощный)
st.set_page_config(page_title="RBS: Глобальное Управление", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #D32F2F !important; font-size: 32px; font-weight: bold; }
    h1, h2, h3 { color: #1A237E !important; font-family: 'Segoe UI', sans-serif; }
    .main-stat { border-left: 5px solid #1A237E; padding-left: 15px; background: #F5F5F5; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        if pd.isna(val): return 0
        return int(float(str(val).replace(' ', '').replace('₽', '').replace(',', '.')))
    except: return 0

def find_col(df, key):
    for c in df.columns:
        if key.lower() in str(c).replace('\n', ' ').lower(): return c
    return None

@st.cache_data(ttl=5)
def load_massive_data():
    try:
        # Берем весь основной массив до 100 строки
        df = pd.read_csv(URL).head(100).fillna(0)
        return df
    except: return pd.DataFrame()

st.title("🏛️ RBS: ЦЕНТР УПРАВЛЕНИЯ СТРУКТУРОЙ")

df_raw = load_massive_data()

if not df_raw.empty:
    # Ключевые колонки структуры
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_exit = find_col(df_raw, 'Тип рег')
    c_kkt = find_col(df_raw, 'ККТ')
    c_fn_used = find_col(df_raw, 'истратил')
    c_sum = find_col(df_raw, 'Сумма')

    # Чистим весь массив данных
    for col in [c_kkt, c_fn_used, c_sum]:
        if col: df_raw[col] = df_raw[col].apply(clean_num)

    # --- ГЛАВНАЯ ПАНЕЛЬ: РАСХОДЫ И ИТОГИ ---
    st.subheader("📊 ОБЩИЕ ПОКАЗАТЕЛИ СТРУКТУРЫ")
    m1, m2, m3 = st.columns(3)
    
    total_spent = df_raw[c_fn_used].sum() if c_fn_used else 0
    total_cash = df_raw[c_sum].sum() if c_sum else 0
    total_stock = df_raw[c_kkt].sum() if c_kkt else 0
    
    m1.metric("ОБЩИЙ РАСХОД ФН", f"{total_spent} шт")
    m2.metric("ДЕНЕЖНЫЙ МАССИВ", f"{total_cash:,.0f} ₽".replace(',', ' '))
    m3.metric("ТЕКУЩИЙ ОСТАТОК", f"{total_stock} шт")

    st.divider()

    # --- АНАЛИТИКА ПО ФИЛИАЛАМ (РАСХОДЫ) ---
    st.subheader("📈 РАСХОД ПО ФИЛИАЛАМ И СП")
    
    if c_sp and c_fn_used:
        # Группируем расход по партнерам
        sp_expense = df_raw.groupby(c_sp)[c_fn_used].sum().reset_index()
        sp_expense = sp_expense[sp_expense[c_fn_used] > 0].sort_values(by=c_fn_used, ascending=False)
        
        fig_expense = px.bar(
            sp_expense, 
            x=c_sp, 
            y=c_fn_used, 
            text_auto=True,
            title="Кто больше всех истратил ФН",
            color=c_fn_used,
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_expense, use_container_width=True)

    # --- МАССИВНЫЕ ФИЛЬТРЫ ---
    with st.expander("🛠️ ГЛУБОКАЯ ФИЛЬТРАЦИЯ МАССИВА"):
        f1, f2 = st.columns(2)
        with f1:
            sel_e = st.multiselect("Тип выезда (удаленно/выезд)", sorted(df_raw[c_exit].unique()))
        with f2:
            sel_city = st.multiselect("Выбор филиалов (города)", sorted(df_raw[c_city].unique()))

        df_filtered = df_raw.copy()
        if sel_e: df_filtered = df_filtered[df_filtered[c_exit].isin(sel_e)]
        if sel_city: df_filtered = df_filtered[df_filtered[c_city].isin(sel_city)]

    # --- ДЕТАЛЬНАЯ ТАБЛИЦА СТРУКТУРЫ ---
    st.subheader("📋 РЕЕСТР ВСЕЙ СТРУКТУРЫ")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

else:
    st.error("Система не видит таблицу. Проверь права доступа!")
