import streamlit as st
import pandas as pd

# --- 1. ПРЕМИУМ ДИЗАЙН LIFE PAY ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ОТГРУЗКИ", page_icon="🚚")

st.markdown("""
<style>
    .stApp { background-color: #F4F7FB; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    .main-header { font-size: 32px; font-weight: 900; color: #0052FF; margin-bottom: 30px; letter-spacing: -1px; }
    
    .ship-card {
        background: white; border-radius: 16px; padding: 25px;
        margin-bottom: 15px; border: 1px solid #E2E8F0;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 20px rgba(0, 82, 255, 0.05);
    }
    
    .date-box { text-align: center; padding-right: 25px; border-right: 2px solid #F1F5F9; min-width: 140px; }
    .date-val { font-size: 18px; font-weight: 900; color: #1E293B; }
    .date-label { font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase; }
    
    .content-box { flex: 3; padding: 0 30px; }
    .org-name { font-size: 19px; font-weight: 800; color: #0052FF; margin-bottom: 5px; }
    .city-tag { background: #EEF2FF; color: #0052FF; padding: 2px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; }
    
    .ttn-btn {
        display: inline-block; padding: 10px 20px; background: #0052FF;
        color: white !important; border-radius: 10px; text-decoration: none;
        font-weight: 700; font-size: 13px; box-shadow: 0 4px 12px rgba(0, 82, 255, 0.2);
    }
    .badge-status { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ ---
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def get_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        df = df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        return df
    except: return pd.DataFrame()

df_raw = get_data()

# --- 3. БЕЛАЯ КОНСОЛЬ ---
with st.sidebar:
    st.markdown("<h1 style='color: #0052FF; margin-bottom:0;'>LIFE PAY</h1>", unsafe_allow_html=True)
    st.markdown("<span class='badge-status'>● В РЕЙТИНГЕ</span>", unsafe_allow_html=True)
    st.divider()
    
    if not df_raw.empty:
        # ГУРОД И ПАРТНЕР ТЕПЕРЬ ИЗ СТОЛБЦА B (Индекс 1)
        city_partner_list = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
        sel_city = st.selectbox("📍 Город / Партнер (Столбец B):", ["Все"] + city_partner_list)
        
        # ОРГАНИЗАЦИЯ ИЗ СТОЛБЦА C (Индекс 2)
        o_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
        sel_org = st.selectbox("🏢 Организация (Столбец C):", ["Все"] + o_list)
        
        search = st.text_input("🔍 Поиск по номеру ТТН:")

# --- 4. ФИЛЬТРАЦИЯ ---
df_f = df_raw.iloc[::-1].copy() # Сначала новые
if not df_raw.empty:
    if sel_city != "Все": df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_city]
    if sel_org != "Все": df_f = df_f[df_f.iloc[:, 2].astype(str) == sel_org]
    if search: df_f = df_f[df_f.iloc[:, 10].astype(str).str.contains(search, case=False)]

# --- 5. ВЫВОД КАРТОЧЕК ---
st.markdown("<div class='main-header'>🚚 Мониторинг отгрузок</div>", unsafe_allow_html=True)

if df_f.empty:
    st.info("Данные не найдены. Проверьте фильтры.")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        # СТОЛБЕЦ L (11) - ДАТА
        send_date = str(row.iloc[11]) if len(row) > 11 else "---"
        # СТОЛБЕЦ C (2) - ОРГАНИЗАЦИЯ
        org = str(row.iloc[2])
        # СТОЛБЕЦ B (1) - ГОРОД
        city = str(row.iloc[1])
        # СТОЛБЕЦ K (10) - ТТН
        ttn = str(row.iloc[10])
        # СТОЛБЕЦ H (7) - СОСТАВ
        content = str(row.iloc[7])
        
        st.markdown(f"""
        <div class="ship-card">
            <div class="date-box">
                <div class="date-val">{send_date}</div>
                <div class="date-label">Дата отправки</div>
            </div>
            <div class="content-box">
                <span class="city-tag">📍 {city}</span>
                <div class="org-name">{org}</div>
                <div style="color: #64748B; font-size: 13px;">Получатель: {row.iloc[4]}</div>
            </div>
            <div class="status-box">
                <a href="{ttn if 'http' in ttn else '#'}" target="_blank" class="ttn-btn">
                    { '🔗 ОТСЛЕДИТЬ' if 'http' in ttn else '📦 ' + ttn }
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🛠 Состав оборудования"):
            st.info(content)
            csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
            st.download_button(f"📥 Excel ТТН {i}", csv, f"r_{idx}.csv", "text/csv", key=f"dl_{idx}")
