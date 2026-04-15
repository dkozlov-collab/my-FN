import streamlit as st, pandas as pd, plotly.express as px, re

# Настройка под широкий экран телефона
st.set_page_config(layout="wide", page_title="RBS GLOBAL SYSTEM")

# Стиль
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #007BFF !important; font-size: 28px; font-weight: bold; }
    h1 { color: #1A237E !important; text-align: center; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ССЫЛКИ
U_SKLAD = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
U_LOGIST = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

# Функция очистки цифр (чтобы буквы не мешали считать итоги)
def get_val(v):
    try:
        n = re.findall(r'\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

# Меню выбора раздела
st.sidebar.title("💎 RBS COMMAND")
m = st.sidebar.radio("ВЫБОР МОДУЛЯ:", ["📦 СКЛАД И ОСТАТКИ", "🚚 ЛОГИСТИКА 2026"])

# Загрузка данных (Склад 80 ст / Логистика 1000 строк)
@st.cache_data(ttl=5)
def load(url, rows):
    return pd.read_csv(url).iloc[:rows, 0:80].fillna("")

if m == "📦 СКЛАД И ОСТАТКИ":
    df = load(U_SKLAD, 500)
    v_col = 5 # Столбец Касс для графиков
    st.markdown("<h1>📦 СКЛАД: ПОЛНЫЙ МАССИВ (80 СТ)</h1>", unsafe_allow_html=True)
else:
    df = load(U_LOGIST, 1000)
    v_col = 11 # Столбец Обязательств для графиков
    st.markdown("<h1>🚚 ЛОГИСТИКА: БЕСКОНЕЧНЫЙ МАССИВ</h1>", unsafe_allow_html=True)

# --- ГЛОБАЛЬНАЯ ФИЛЬТРАЦИЯ ПО ВСЕМУ ---
st.sidebar.subheader("🔍 Фильтрация")
f_search = st.sidebar.text_input("Поиск (номер/имя/город):")
f_p = st.sidebar.multiselect("Партнеры (Отправители):", sorted(df.iloc[:, 1].unique().astype(str)))
f_c = st.sidebar.multiselect("Города (Получатели):", sorted(df.iloc[:, 2].unique().astype(str)))

# Применяем фильтры
if f_search:
    df = df[df.apply(lambda r: r.astype(str).str.contains(f_search, case=False).any(), axis=1)]
if f_p:
    df = df[df.iloc[:, 1].astype(str).isin(f_p)]
if f_c:
    df = df[df.iloc[:, 2].astype(str).isin(f_c)]

# --- ИТОГИ ---
total = df.iloc[:, v_col].apply(get_val).sum()
c1, c2 = st.columns(2)
c1.metric("ИТОГО ПО ВЫБОРКЕ", f"{total:,.0f}".replace(',',' '))
c2.metric("ВСЕГО СТРОК", len(df))

# Основная таблица (Ширина 80 столбцов)
st.dataframe(df, use_container_width=True, height=500)

# ГРАФИКИ
if total > 0:
    st.write("### 📊 Аналитика")
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.pie(df, values=df.iloc[:, v_col].apply(get_val), names=df.columns[1], hole=0.5, title="Доли по Партнерам")
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.bar(df, x=df.columns[2], y=df.iloc[:, v_col].apply(get_val), title="Распределение по Городам")
        st.plotly_chart(fig2, use_container_width=True)
