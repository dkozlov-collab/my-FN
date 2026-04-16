import streamlit as st
import pandas as pd

# --- 1. ПРЕМИУМ ДИЗАЙН LIFE PAY ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ОТГРУЗКИ", page_icon="🚚")

st.markdown("""
<style>
    .stApp { background-color: #F4F7FB; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    
    .main-header { font-size: 32px; font-weight: 900; color: #0052FF; margin-bottom: 30px; letter-spacing: -1px; }
    
    /* СТИЛЬ ПРЕМИУМ КАРТОЧКИ */
    .ship-card {
        background: white; border-radius: 16px; padding: 25px;
        margin-bottom: 15px; border: 1px solid #E2E8F0;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 20px rgba(0, 82, 255, 0.05);
        transition: all 0.3s ease;
    }
    .ship-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0, 82, 255, 0.1); border-color: #0052FF; }
    
    .date-box { text-align: center; padding-right: 25px; border-right: 2px solid #F1F5F9; min-width: 120px; }
    .date-day { font-size: 24px; font-weight: 900; color: #1E293B; line-height: 1; }
    .date-month { font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 700; }
    
    .content-box { flex: 3; padding: 0 30px; }
    .org-name { font-size: 18px; font-weight: 800; color: #1E293B; margin-bottom: 5px; }
    .partner-tag { background: #EEF2FF; color: #0052FF; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    
    .status-box { flex: 1; text-align: right; }
    .ttn-btn {
        display: inline-block; padding: 10px 20px; background: #0052FF;
        color: white !important; border-radius: 10px; text-decoration: none;
        font-weight: 700; font-size: 14px; box-shadow: 0 4px 12px rgba(0, 82, 255, 0.3);
    }
    .city-badge { color: #64748B; font-weight: 700; font-size: 13px; display: block; margin-top: 8px; }
    
    /* ТЕГИ ДЛЯ СЕРИЙНИКОВ */
    .sn-tag {
        display: inline-block; background: #F1F5F9; color: #475569;
        padding: 2px 10px; border-radius: 20px; font-size: 11px;
        margin: 2px; border: 1px solid #E2E8F0; font-family: monospace;
    }
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
    st.markdown("<div style='color: #166534; font-weight:700; font-size:12px;'>● В РЕЙТИНГЕ</div>", unsafe_allow_html=True)
    st.divider()
    
    if not df_raw.empty:
        # Умные фильтры
        all_partners = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
        sel_part = st.selectbox("🤝 Партнер:", ["Все"] + all_partners)
        
        all_orgs = sorted([str(x) for x in df_raw.iloc[:, 5].unique() if str(x).strip() and str(x) != "0"])
        sel_org = st.selectbox("🏢 Организация:", ["Все"] + all_orgs)
        
        search = st.text_input("🔍 Поиск по ТТН:")
    
    st.divider()
    st.write("v 5.0 Premium")

# --- 4. ФИЛЬТРАЦИЯ ---
df_f = df_raw.iloc[::-1].copy() # Новые вверх
if not df_raw.empty:
    if sel_part != "Все": df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_part]
    if sel_org != "Все": df_f = df_f[df_f.iloc[:, 5].astype(str) == sel_org]
    if search: df_f = df_f[df_f.iloc[:, 10].astype(str).str.contains(search, case=False)]

# --- 5. ВЫВОД КАРТОЧЕК ---
st.markdown("<div class='main-header'>🚚 Мониторинг отгрузок</div>", unsafe_allow_html=True)
if df_f.empty:
    st.info("Отгрузок не найдено")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        # Парсим дату
        d_str = str(row.iloc[0])
        day = d_str[8:10] if len(d_str) > 9 else "---"
        month = "АПРЕЛЬ" if ".04." in d_str or "-04-" in d_str else "ДАТА" # Упрощенно
        
        ttn = str(row.iloc[10])
        org = str(row.iloc[5])
        partner = str(row.iloc[1])
        city = str(row.iloc[3])
        content = str(row.iloc[7])
        
        # HTML КАРТОЧКИ
        st.markdown(f"""
        <div class="ship-card">
            <div class="date-box">
                <div class="date-day">{day}</div>
                <div class="date-month">{month}</div>
            </div>
            <div class="content-box">
                <span class="partner-tag">{partner}</span>
                <div class="org-name">{org}</div>
                <div style="color: #64748B; font-size: 13px;">Получатель: {row.iloc[4]}</div>
            </div>
            <div class="status-box">
                <a href="{ttn if 'http' in ttn else '#'}" target="_blank" class="ttn-btn">
                    { '🔗 ОТСЛЕДИТЬ' if 'http' in ttn else '📦 ' + ttn }
                </a>
                <span class="city-badge">📍 {city}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # СКРЫТЫЙ БЛОК (Оборудование и серийники)
        with st.expander("🛠 Состав оборудования и серийные номера"):
            st.write("Детали состава:")
            st.info(content)
            
            # Пытаемся вытащить серийники (если они через запятую или пробел)
            st.write("Серийные номера (теги):")
            serials = content.replace(',', ' ').split()
            tags_html = "".join([f'<span class="sn-tag"># {s}</span>' for s in serials if len(s) > 5])
            st.markdown(tags_html if tags_html else "Индивидуальные номера не найдены", unsafe_allow_html=True)
            
            st.divider()
            csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
            st.download_button(f"📥 Скачать Excel-карточку ТТН {i}", csv, f"ship_{idx}.csv", "text/csv", key=f"dl_{idx}")
