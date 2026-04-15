import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="RBS: Мониторинг", layout="wide", page_icon="📊")

# Твоя актуальная ссылка
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    """Превращает любой мусор в таблице в чистое число"""
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except:
        return 0

def find_col(df, possible_names):
    """Ищет колонку в таблице, даже если в названии лишние пробелы"""
    for name in possible_names:
        for actual_col in df.columns:
            if name.lower().strip() == actual_col.lower().strip():
                return actual_col
    return None

@st.cache_data(ttl=15)
def load_data():
    try:
        df = pd.read_csv(URL).fillna(0)
        # Ограничиваемся первыми 85 строками, чтобы не цеплять мусор снизу
        df = df.head(85)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа к Google Таблице: {e}")
        return pd.DataFrame()

# --- ПУЛЬТ УПРАВЛЕНИЯ ---
st.markdown("<h1 style='text-align: center;'>💎 РЕГИСТРАЦИЯ ОБОРУДОВАНИЯ RBS</h1>", unsafe_allow_html=True)
# Настройка стиля 2026
st.set_page_config(page_title="RBS: Склад и Логистика", layout="wide", page_icon="🚀")

# Твоя ссылка (проверь доступ "Все, у кого есть ссылка"!)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=15)
def load_all_data():
    try:
        full_df = pd.read_csv(URL).fillna("")
        # Массив Склада (1-80)
        df_stock = full_df.iloc[0:80].copy()
        # Массив Логистики (150+)
        df_logic = full_df.iloc[149:].copy()
        return df_stock, df_logic
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- ВЕРХНЕЕ МЕНЮ ---
st.sidebar.title("💎 RBS HUB 2026")
mode = st.sidebar.radio("Выберите раздел:", ["📊 Остатки ККТ", "🚚 Логистика (150+)"])

df_s, df_l = load_all_data()

# ================= РАЗДЕЛ: СКЛАДЫ =================
if mode == "📊 Остатки ККТ":
    st.markdown("<h1 style='text-align: center;'>🏙️ МОНИТОРИНГ СКЛАДОВ</h1>", unsafe_allow_html=True)
    
    if not df_s.empty:
        # KPI
        c1, c2 = st.columns(2)
        # Чистим числа для графиков
        df_s['Остатки ККТ'] = pd.to_numeric(df_s['Остатки ККТ'].astype(str).str.replace(' ',''), errors='coerce').fillna(0)
        
        c1.metric("📦 ВСЕГО ККТ", f"{int(df_s['Остатки ККТ'].sum())} шт")
        c2.metric("🏙️ ГОРОДОВ", len(df_s[df_s['Остатки ККТ'] > 0]))

        # Модный круг
        fig = px.pie(df_s[df_s['Остатки ККТ'] > 0], values='Остатки ККТ', names='Склад', hole=0.6)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_s, use_container_width=True)

# ================= РАЗДЕЛ: ЛОГИСТИКА =================
else:
    st.markdown("<h1 style='text-align: center; color: #FFA500;'>📦 ОТГРУЗКИ И ПОСЫЛКИ</h1>", unsafe_allow_html=True)
    
    if not df_l.empty:
        search = st.text_input("🔍 Быстрый поиск по логистике (город, трек, комплект)...")
        if search:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # РИСУЕМ КВАДРАТИКИ (ПЛИТКИ)
        st.write("### 🚚 Статус отгрузок (Плитки)")
        
        # Берем первые 3 колонки для плитки: Комплект, Куда, Статус/Трек
        items = df_l.values.tolist()
        for i in range(0, len(items), 4):
            cols = st.columns(4)
            for j, item in enumerate(items[i:i+4]):
                with cols[j]:
                    st.markdown(f"""
                    <div style="border: 2px solid #FFA500; border-radius: 10px; padding: 10px; background-color: #1E1E1E; margin-bottom: 10px;">
                        <span style="color: #FFA500; font-weight: bold;">📦 Посылка:</span><br>
                        <span style="font-size: 16px;">{item[0]}</span><br>
                        <small>📍 {item[1] if len(item)>1 else ""}</small><br>
                        <code style="color: #00ffcc;">{item[2] if len(item)>2 else ""}</code>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.write("### 📋 Полный реестр логистики")
        st.dataframe(df_l, use_container_width=True)
    else:
        st.warning("На 150-й строке данных не обнаружено.")


df_raw = load_data()

if not df_raw.empty:
    # Ищем важные колонки
    col_kkt = find_col(df_raw, ['Остатки ККТ', 'ККТ', 'Остаток ККТ'])
    col_partner = find_col(df_raw, ['Сервис Партнер', 'Партнер'])
    col_money = find_col(df_raw, ['Итого сумма', 'Итого', 'Сумма'])
    col_city = find_col(df_raw, ['Склад', 'Город'])

    # Чистим данные
    if col_kkt: df_raw[col_kkt] = df_raw[col_kkt].apply(clean_num)
    if col_money: df_raw[col_money] = df_raw[col_money].apply(clean_num)

    # --- ФИЛЬТРАЦИЯ ---
    st.sidebar.header("Фильтры")
    if col_partner:
        partners = ["ВСЕ ПАРТНЕРЫ"] + sorted([str(p) for p in df_raw[col_partner].unique() if p != 0 and p != "0"])
        sel_p = st.sidebar.selectbox("Выберите Партнера:", partners)
        df = df_raw[df_raw[col_partner] == sel_p] if sel_p != "ВСЕ ПАРТНЕРЫ" else df_raw
    else:
        df = df_raw

    # --- KPI ---
    c1, c2 = st.columns(2)
    total_kkt = df[col_kkt].sum() if col_kkt else 0
    c1.metric("📦 ВСЕГО ККТ", f"{total_kkt} шт")
    
    total_money = df[col_money].sum() if col_money else 0
    c2.metric("💰 КАПИТАЛ", f"{total_money:,.0f} ₽".replace(',', ' '))

    st.divider()

    # --- ГРАФИКИ ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### 🍩 Доли по складам")
        if col_kkt and col_city and total_kkt > 0:
            fig_pie = px.pie(df[df[col_kkt] > 0], values=col_kkt, names=col_city, hole=0.5)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Нет данных для круга")

    with col_r:
        st.write("### 📊 Наличие (Топ-10)")
        if col_kkt and col_city and total_kkt > 0:
            top_cities = df.nlargest(10, col_kkt)
            fig_bar = px.bar(top_cities, x=col_city, y=col_kkt, color=col_kkt, text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    # ТАБЛИЦА
    st.subheader("📋 Реестр данных")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ Таблица пуста. Проверь настройки доступа в Google Sheets (Доступ 'Все, у кого есть ссылка').")
    st.set_page_config(page_title="LOGISTICS: Посылки", layout="wide", page_icon="🚚")
URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/edit?pli=1&gid=0#gid=0"

# Читаем данные со 150 строки (пропускаем 149)
df_log = pd.read_csv(URL, skiprows=149).fillna("")

