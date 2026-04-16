import streamlit as st
import pandas as pd
import re

# --- 1. ВИЗУАЛЬНОЕ ОФОРМЛЕНИЕ ---
st.set_page_config(layout="wide", page_title="RBS LOGISTICS PRO", page_icon="🚚")

st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    .main-header { font-size: 32px; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 30px; }
    .card { 
        background: white; border-radius: 12px; padding: 20px; 
        margin-bottom: 20px; border: 1px solid #DEE2E6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .click-btn {
        display: inline-block; padding: 8px 16px; background-color: #2563EB;
        color: white !important; border-radius: 6px; text-decoration: none;
        font-weight: bold; font-size: 13px; margin-top: 5px; margin-right: 5px;
    }
    .city-label { background-color: #E0E7FF; color: #3730A3; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 700; }
    .status-text { font-size: 13px; color: #059669; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ ---
# Твоя ссылка на экспорт Google Таблицы (Логистика)
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5) # Обновление каждые 5 секунд для "живого" эффекта
def get_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        # Фильтруем пустые строки (проверка по 2-му столбцу "Партнер")
        df = df[df.iloc[:, 1].astype(str).str.strip() != ""]
        # Преобразование даты
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()

df_all = get_data()

# --- 3. ЛОГИКА ФИЛЬТРАЦИИ ---
st.markdown("<div class='main-header'>🚚 Система логистики RBS (Полный функционал)</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ ФИЛЬТРЫ")
    
    # 1. Город (Столбец 4, индекс 3)
    cities = sorted([str(x) for x in df_all.iloc[:, 3].unique() if x])
    sel_city = st.selectbox("📍 Выберите город:", ["Все города"] + cities)
    
    # 2. Получатель (Склейка 5 и 6 столбцов)
    df_all['Full_Name'] = (df_all.iloc[:, 4].astype(str) + " | " + df_all.iloc[:, 5].astype(str)).str.replace("0", "").str.strip(" | ")
    recs = sorted([str(x) for x in df_all['Full_Name'].unique() if x])
    sel_rec = st.selectbox("🏢 Получатель / Компания:", ["Все получатели"] + recs)
    
    st.divider()
    st.info("Данные подгружаются напрямую из Google Таблицы в режиме реального времени.")

# Панель быстрого поиска и дат
c1, c2 = st.columns([1, 2])
with c1:
    d_range = st.date_input("📅 Период отгрузок:", [])
with c2:
    search_query = st.text_input("🔍 Глобальный поиск (ТТН, серийник, название товара):")

# Применяем фильтры
df_f = df_all.copy()

if sel_city != "Все города":
    df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]
if sel_rec != "Все получатели":
    df_f = df_f[df_f['Full_Name'] == sel_rec]
if len(d_range) == 2:
    df_f = df_f[(df_f.iloc[:, 0].dt.date >= d_range[0]) & (df_f.iloc[:, 0].dt.date <= d_range[1])]
if search_query:
    df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

# --- 4. ОТОБРАЖЕНИЕ ---
st.write(f"Отображено записей: {len(df_f)}")

# Кнопка Excel для всего списка
if not df_f.empty:
    csv_all = df_f.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Выгрузить текущий список в Excel", csv_all, "logistics_report.csv", "text/csv")

st.divider()

# Плиточный интерфейс карточек
if df_f.empty:
    st.warning("Ничего не найдено. Проверьте параметры фильтров.")
else:
    rows_count = len(df_f)
    cols = st.columns(3) # В 3 колонки
    
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 3]:
            # Обработка ТТН и Ссылок
            ttn_val = str(row.iloc[10]) # Столбец K (11-й)
            status_val = str(row.iloc[11]) if len(row) > 11 else "" # Столбец L
            
            # Генерация кликабельных кнопок, если есть http
            btns_html = ""
            if "http" in ttn_val:
                btns_html += f'<a href="{ttn_val}" target="_blank" class="click-btn">🔗 Накладная ТТН</a>'
            else:
                btns_html += f"<div style='font-weight:bold; color:#1E3A8A; margin-bottom:5px;'>📦 ТТН: {ttn_val}</div>"
            
            if "http" in status_val:
                btns_html += f'<a href="{status_val}" target="_blank" class="click-btn">📍 Статус груза</a>'

            st.markdown(f"""
            <div class="card">
                <div style="margin-bottom:10px;">{btns_html}</div>
                <div style="font-size:16px; font-weight:700; color:#334155;">{row['Full_Name']}</div>
                <div style="margin-top:12px;">
                    <span class="city-label">📍 {row.iloc[3]}</span>
                    <span style="font-size:12px; color:#64748B; margin-left:10px;">
                        📅 {row.iloc[0].strftime('%d.%m.%Y') if pd.notnull(row.iloc[0]) else 'Без даты'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Выпадающий список с составом и кнопкой Excel для конкретной строки
            with st.expander("📦 Детали оборудования"):
                st.write(f"Состав: {row.iloc[7]}")
                st.write(f"Комментарий: {row.iloc[12] if len(row) > 12 else 'Нет'}")
                
                row_csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Excel этой строки", row_csv, f"order_{idx}.csv", "text/csv", key=f"dl_{idx}")
