import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под мобильные устройства и Pocophone
st.set_page_config(page_title="RBS: Mobile Analytics", layout="wide")

# Светлый, чистый дизайн (под "белый Pocophone")
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-weight: bold; }
    .stSelectbox, .stMultiSelect { background-color: white !important; }
    h1, h2, h3 { color: #343A40 !important; }
    .filter-container { border: 1px solid #DEE2E6; padding: 10px; border-radius: 10px; background: white; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

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
def load_full_data():
    try:
        df = pd.read_csv(URL).head(100).fillna(0)
        # Чистим все важные колонки
        for col in df.columns:
            if any(x in col.lower() for x in ['ккт', 'фн', 'сумма', 'пути', 'выезд']):
                df[col] = df[col].apply(clean_num)
        return df
    except: return pd.DataFrame()

df_raw = load_full_data()

if not df_raw.empty:
    # Ищем колонки
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_exit = find_col(df_raw, 'Выезд')
    c_kkt = find_col(df_raw, 'ККТ')
    c_fn_way = find_col(df_raw, 'пути') # Колонка ФН в пути

    # --- БЛОК ФИЛЬТРОВ ---
    st.markdown("### 🔍 Система фильтров")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        plist = ["Все партнеры"] + sorted(list(df_raw[c_sp].unique())) if c_sp else ["Все"]
        sel_p = st.selectbox("Партнер", plist)
    with f2:
        clist = ["Все склады"] + sorted(list(df_raw[c_city].unique())) if c_city else ["Все"]
        sel_c = st.selectbox("Склад/Город", clist)
    with f3:
        elist = ["Все выезды"] + sorted(list(df_raw[c_exit].unique().astype(str))) if c_exit else ["Все"]
        sel_e = st.selectbox("Тип выезда", elist)

    # Применение фильтров
    df_f = df_raw.copy()
    if sel_p != "Все партнеры": df_f = df_f[df_f[c_sp] == sel_p]
    if sel_c != "Все склады": df_f = df_f[df_f[c_city] == sel_c]
    if sel_e != "Все выезды": df_f = df_f[df_f[c_exit].astype(str) == sel_e]

    # --- ИТОГИ ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    total_kkt = df_f[c_kkt].sum() if c_kkt else 0
    way_fn = df_f[c_fn_way].sum() if c_fn_way else 0
    
    m1.metric("📦 ККТ в наличии", f"{total_kkt} шт")
    m2.metric("🚚 ФН в пути", f"{way_fn} шт")
    m3.metric("🏢 Складов активно", len(df_f[df_f[c_kkt]>0]))

    # --- ГРАФИКИ ---
    st.divider()
    col_graph_l, col_graph_r = st.columns(2)
    
    with col_graph_l:
        st.write("### 🍩 Доли по партнерам")
        if total_kkt > 0:
            fig_p = px.pie(df_f[df_f[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_p, use_container_width=True)
            
    with col_graph_r:
        st.write("### 🚛 Отправленные ФН (В пути)")
        if way_fn > 0:
            fig_w = px.bar(df_f[df_f[c_fn_way]>0], x=c_city, y=c_fn_way, text_auto=True, color_discrete_sequence=['#FFC107'])
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            st.info("Нет ФН в пути по выбранным фильтрам")

    # --- ТАБЛИЦА ---
    st.divider()
    st.write("### 📋 Детальная таблица (Склад 1-100)")
    st.dataframe(df_f, use_container_width=True, hide_index=True)

else:
    st.error("Данные не загружены. Проверь доступ к Google Таблице!")
