import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка под мобильный (Pocophone Style)
st.set_page_config(page_title="RBS: Mobile", layout="wide")

# Светлый дизайн
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #212529; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; }
    .stSelectbox, .stMultiSelect { background-color: #F8F9FA !important; }
    h1, h2, h3 { color: #343A40 !important; font-family: sans-serif; }
    .stDataFrame { border: 1px solid #EEE; }
</style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

def find_col(df, key):
    """Ищет колонку, игнорируя регистр и переносы строк"""
    for c in df.columns:
        if key.lower() in str(c).replace('\n', ' ').lower():
            return c
    return None

@st.cache_data(ttl=10)
def load_full_data():
    try:
        df = pd.read_csv(URL).head(150).fillna(0)
        # Чистим все числовые колонки (ККТ, ФН, Пути)
        for col in df.columns:
            if any(x in col.lower() for x in ['ккт', 'фн', 'пути', 'выезд', 'сумма']):
                df[col] = df[col].apply(clean_num)
        return df
    except: return pd.DataFrame()

st.title("📱 RBS Мониторинг")

df_raw = load_full_data()

if not df_raw.empty:
    # Ищем колонки динамически
    c_sp = find_col(df_raw, 'Партнер')
    c_city = find_col(df_raw, 'Склад')
    c_exit = find_col(df_raw, 'Тип рег') # Это поле "выезд"
    c_kkt = find_col(df_raw, 'Остатки ККТ')
    c_fn15 = find_col(df_raw, 'Остатки ФН-15')
    c_way = find_col(df_raw, 'В пути ККТ')

    # --- СИСТЕМА ФИЛЬТРОВ ---
    st.markdown("### 🔍 Фильтры")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        # Безопасное создание списка партнеров (без ошибок сортировки)
        p_unique = [str(x) for x in df_raw[c_sp].unique() if x != 0 and x != ""] if c_sp else []
        sel_p = st.selectbox("Партнер", ["Все"] + sorted(p_unique))
    with f2:
        c_unique = [str(x) for x in df_raw[c_city].unique() if x != 0 and x != ""] if c_city else []
        sel_c = st.selectbox("Склад", ["Все"] + sorted(c_unique))
    with f3:
        e_unique = [str(x) for x in df_raw[c_exit].unique() if x != 0 and x != ""] if c_exit else []
        sel_e = st.selectbox("Тип выезда", ["Все"] + sorted(e_unique))

    # Применение фильтров
    df_f = df_raw.copy()
    if sel_p != "Все": df_f = df_f[df_f[c_sp].astype(str) == sel_p]
    if sel_c != "Все": df_f = df_f[df_f[c_city].astype(str) == sel_c]
    if sel_e != "Все": df_f = df_f[df_f[c_exit].astype(str) == sel_e]

    # --- ЦИФРЫ ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    tkkt = df_f[c_kkt].sum() if c_kkt else 0
    tfn = df_f[c_fn15].sum() if c_fn15 else 0
    tway = df_f[c_way].sum() if c_way else 0
    
    m1.metric("📦 ККТ", f"{tkkt} шт")
    m2.metric("📑 ФН-15", f"{tfn} шт")
    m3.metric("🚛 В ПУТИ", f"{tway} шт")

    # --- ГРАФИКИ (Чистый дизайн) ---
    st.divider()
    g1, g2 = st.columns(2)
    
    with g1:
        st.write("#### Доли по ККТ")
        if tkkt > 0:
            fig1 = px.pie(df_f[df_f[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.5, 
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
            
    with g2:
        st.write("#### Наличие по городам")
        if tkkt > 0:
            top_df = df_f.nlargest(10, c_kkt)
            st.bar_chart(top_df.set_index(c_city)[c_kkt])

    # --- ТАБЛИЦА ---
    st.write("#### 📋 Детальный реестр")
    st.dataframe(df_f, use_container_width=True, hide_index=True)

else:
    st.error("Ошибка! Проверь доступ в Google Таблице (кнопка 'Поделиться').")
