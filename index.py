import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка стиля 2026 (Тренды: Темная тема + Неон)
st.set_page_config(page_title="RBS Global 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 0 0 10px #00E5FF; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: #161A24; border-radius: 10px; padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)

# 2. Твои ссылки
URL_STOCK = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"
URL_LOGIC = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key_word):
    """Ищет колонку по ключевому слову, игнорируя переносы строк и пробелы"""
    for col in df.columns:
        if key_word.lower() in col.replace('\n', ' ').lower():
            return col
    return None

@st.cache_data(ttl=10)
def load_data(url, rows=None, skip=0):
    try:
        df = pd.read_csv(url, skiprows=skip).fillna(0)
        if rows: df = df.head(rows)
        return df
    except: return pd.DataFrame()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.markdown("<h1 style='text-align: center;'>🛰️ RBS: МОНИТОРИНГ И ЛОГИСТИКА 2026</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 СКЛАД (1-80)", "🚚 ЛОГИСТИКА (1150+)"])

# --- ВКЛАДКА 1: СКЛАД ---
with tab1:
    df1 = load_data(URL_STOCK, rows=80)
    if not df1.empty:
        # Авто-поиск колонок (решает проблему KeyError)
        col_kkt = find_col(df1, 'Остатки ККТ')
        col_sum = find_col(df1, 'Сумма')
        col_sp = find_col(df1, 'Партнер')
        col_city = find_col(df1, 'Склад')

        if col_kkt:
            df1[col_kkt] = df1[col_kkt].apply(clean_num)
            total = df1[col_kkt].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("📦 ВСЕГО ККТ", f"{total} шт")
            if col_sum:
                df1[col_sum] = df1[col_sum].apply(clean_num)
                c2.metric("💰 ОБЩИЙ КАПИТАЛ", f"{df1[col_sum].sum():,.0f} ₽".replace(',', ' '))

            st.divider()

            # Трендовая аналитика (Крутой Бублик)
            col_graph1, col_graph2 = st.columns(2)
            with col_graph1:
                st.write("### 🍩 Доли Партнеров")
                if col_sp and total > 0:
                    fig = px.pie(df1[df1[col_kkt] > 0], values=col_kkt, names=col_sp, hole=0.7)
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_graph2:
                st.write("### 📊 Топ Городов")
                if col_city:
                    top_df = df1.nlargest(10, col_kkt)
                    fig_bar = px.bar(top_df, x=col_city, y=col_kkt, color=col_kkt, text_auto=True)
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        st.dataframe(df1, use_container_width=True)

# --- ВКЛАДКА 2: ЛОГИСТИКА ---
with tab2:
    df2 = load_data(URL_LOGIC, skip=1149)
    if not df2.empty:
        st.subheader("🏢 Реестр отгрузок (Вид: Большой Excel)")
        search = st.text_input("🔍 Поиск по серийнику или городу...")
        if search:
            df2 = df2[df2.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(df2, use_container_width=True)
    else:
        st.error("❌ Таблица логистики недоступна. Проверь доступ к ссылке!")
