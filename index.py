import streamlit as st
import pandas as pd
import re

# --- 1. НАСТРОЙКИ ДИЗАЙНА ---
st.set_page_config(layout="wide", page_title="RBS LOGISTICS PRO")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    .main-header { font-size: 30px; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 20px; }
    .card { 
        background: white; border-radius: 12px; padding: 18px; 
        margin-bottom: 15px; border: 1px solid #DEE2E6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .click-btn {
        display: inline-block; padding: 6px 12px; background-color: #2563EB;
        color: white !important; border-radius: 6px; text-decoration: none;
        font-weight: 600; font-size: 13px; margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ (БЕЗОПАСНАЯ) ---
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/edit?usp=sharing"

@st.cache_data(ttl=5)
def get_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        # Убираем полностью пустые строки
        df = df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        if not df.empty:
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except:
        return pd.DataFrame()

df_all = get_data()

st.markdown("<div class='main-header'>🚚 Система логистики RBS</div>", unsafe_allow_html=True)

if df_all.empty:
    st.error("⚠️ Данные не загружены. Проверь таблицу или интернет.")
    st.stop()

# --- 3. ФИЛЬТРЫ ---
with st.sidebar:
    st.header("⚙️ Фильтры")
    
    # Безопасный город (индекс 3)
    if df_all.shape[1] > 3:
        cities = sorted([str(x) for x in df_all.iloc[:, 3].unique() if str(x).strip() and str(x) != "0"])
        sel_city = st.selectbox("📍 Город:", ["Все"] + cities)
    else:
        sel_city = "Все"

    # Безопасный получатель (склейка индексов 4 и 5)
    if df_all.shape[1] > 5:
        df_all['Full_Name'] = (df_all.iloc[:, 4].astype(str) + " | " + df_all.iloc[:, 5].astype(str)).str.replace("0", "").str.strip(" | ")
        recs = sorted([str(x) for x in df_all['Full_Name'].unique() if str(x).strip() and str(x) != "0"])
        sel_rec = st.selectbox("🏢 Получатель:", ["Все"] + recs)
    else:
        df_all['Full_Name'] = "Не указано"
        sel_rec = "Все"

# Поиск и даты
c1, c2 = st.columns([1, 2])
with c1: d_range = st.date_input("📅 Период:", [])
with c2: search_q = st.text_input("🔍 Поиск (ТТН, серийник):")

# Применяем фильтры
df_f = df_all.copy()
if sel_city != "Все": df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]
if sel_rec != "Все": df_f = df_f[df_f['Full_Name'] == sel_rec]
if len(d_range) == 2:
    df_f = df_f[(df_f.iloc[:, 0].dt.date >= d_range[0]) & (df_f.iloc[:, 0].dt.date <= d_range[1])]
if search_q:
    df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]

# --- 4. ВЫВОД КАРТОЧЕК ---
st.write(f"Найдено: {len(df_f)}")

if not df_f.empty:
    csv_all = df_f.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Скачать всё в Excel", csv_all, "logistics.csv", "text/csv")

st.divider()

cols = st.columns(3)
for i, (idx, row) in enumerate(df_f.iterrows()):
    with cols[i % 3]:
        # Безопасный доступ к ТТН (индекс 10) и Статусу (индекс 11)
        ttn = str(row.iloc[10]) if df_all.shape[1] > 10 else ""
        status = str(row.iloc[11]) if df_all.shape[1] > 11 else ""
        
        btns = ""
        if "http" in ttn: btns += f'<a href="{ttn}" target="_blank" class="click-btn">🔗 Накладная</a>'
        else: btns += f"<div style='font-weight:bold; color:#1E3A8A;'>📦 ТТН: {ttn}</div>"
        
        if "http" in status: btns += f'<a href="{status}" target="_blank" class="click-btn">📍 Статус</a>'
    st.markdown(f"""
        <div class="card">
            <div style="margin-bottom:10px;">{btns}</div>
            <div style="font-size:15px; font-weight:700;">{row.get('Full_Name', '---')}</div>
            <div style="margin-top:10px; font-size:12px; color:gray;">
                📅 {row.iloc[0].strftime('%d.%m.%Y') if pd.notnull(row.iloc[0]) else ''} | 
                📍 {row.iloc[3] if df_all.shape[1] > 3 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with st.expander("📁 Детали"):
            st.write(f"Состав: {row.iloc[7] if df_all.shape[1] > 7 else '---'}")
            row_csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel", row_csv, f"row_{idx}.csv", "text/csv", key=f"btn_{idx}")
