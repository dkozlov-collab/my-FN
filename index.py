import streamlit as st
import pandas as pd
import re

# --- 1. КРАСИВЫЙ ДИЗАЙН ---
st.set_page_config(layout="wide", page_title="RBS LOGISTICS PRO", page_icon="🚚")

st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    .main-header { font-size: 30px; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 25px; }
    .card { 
        background: white; border-radius: 12px; padding: 20px; 
        margin-bottom: 15px; border: 1px solid #DEE2E6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .click-btn {
        display: inline-block; padding: 8px 16px; background-color: #2563EB;
        color: white !important; border-radius: 6px; text-decoration: none;
        font-weight: bold; font-size: 13px; margin-right: 5px;
    }
    .city-badge { background-color: #E0E7FF; color: #3730A3; padding: 4px 10px; border-radius: 10px; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 2. УМНАЯ ЗАГРУЗКА ДАННЫХ ---
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def get_clean_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        # Убираем совсем пустые строки
        df = df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        # Пытаемся сделать первый столбец датой
        if not df.empty:
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except Exception as e:
        return pd.DataFrame()

df_all = get_clean_data()

# --- 3. ГЛАВНЫЙ ИНТЕРФЕЙС ---
st.markdown("<div class='main-header'>🚚 Система логистики RBS</div>", unsafe_allow_html=True)

if df_all.empty:
    st.error("⚠️ Не удалось загрузить данные. Проверь ссылку на Google Таблицу или доступ.")
    st.stop()

# --- 4. ФИЛЬТРЫ В САЙДБАРЕ ---
with st.sidebar:
    st.header("⚙️ НАСТРОЙКИ")
    
    # Безопасный фильтр по городам (проверяем наличие 4-го столбца)
    if df_all.shape[1] >= 4:
        cities = sorted([str(x) for x in df_all.iloc[:, 3].unique() if str(x).strip() and str(x) != "0"])
        sel_city = st.selectbox("📍 Город отправки:", ["Все города"] + cities)
    else:
        sel_city = "Все города"

    # Безопасный фильтр по Получателю (проверяем наличие 5 и 6 столбцов)
    if df_all.shape[1] >= 6:
        df_all['Full_Name'] = (df_all.iloc[:, 4].astype(str) + " | " + df_all.iloc[:, 5].astype(str)).str.replace("0", "").str.strip(" | ")
        recs = sorted([str(x) for x in df_all['Full_Name'].unique() if str(x).strip() and str(x) != "0"])
        sel_rec = st.selectbox("🏢 Получатель / Компания:", ["Все получатели"] + recs)
    else:
        df_all['Full_Name'] = "Не указано"
        sel_rec = "Все получатели"

    st.divider()
    st.info("Данные обновляются автоматически.")

# Панель поиска
c1, c2 = st.columns([1, 2])
with c1:
    d_range = st.date_input("📅 Период:", [])
with c2:
    search_query = st.text_input("🔍 Быстрый поиск (ТТН, серийник, товар):")

# --- 5. ПРИМЕНЕНИЕ ФИЛЬТРОВ ---
df_f = df_all.copy()

if sel_city != "Все города":
    df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]
if sel_rec != "Все получатели":
    df_f = df_f[df_f['Full_Name'] == sel_rec]
if len(d_range) == 2:
    df_f = df_f[(df_f.iloc[:, 0].dt.date >= d_range[0]) & (df_f.iloc[:, 0].dt.date <= d_range[1])]
if search_query:
    df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

# --- 6. ОТОБРАЖЕНИЕ КАРТОЧЕК ---
st.write(f"Найдено записей: {len(df_f)}")

if not df_f.empty:
    # Кнопка общего Excel
    csv_all = df_f.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Выгрузить список в Excel", csv_all, "logistics_report.csv", "text/csv
