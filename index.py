import streamlit as st
import pandas as pd

# --- 1. СТИЛЬ МИНИМАЛИЗМА ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    
    /* СТИЛЬ КОМПАКТНОЙ КАРТОЧКИ */
    .compact-row {
        background: white;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .main-text { font-size: 16px; font-weight: 700; color: #1E293B; }
    .sub-text { font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .tag-city { background: #F1F5F9; color: #475569; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    
    /* Оформление серийников внутри */
    .sn-block {
        background: #F8FAFC; border-left: 3px solid #0052FF;
        padding: 10px; border-radius: 4px; font-family: monospace; font-size: 13px;
    }
    .ttn-link {
        background: #0052FF; color: white !important; padding: 8px 16px;
        border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ДАННЫЕ ---
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        return df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
    except: return pd.DataFrame()

df_raw = load_data()

# --- 3. ФИЛЬТРЫ ---
with st.sidebar:
    st.markdown("<h2 style='color:#0052FF'>LIFE PAY</h2>", unsafe_allow_html=True)
    if not df_raw.empty:
        # Организация (C)
        orgs = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
        sel_org = st.selectbox("🏢 Организация:", ["Все"] + orgs)
        # Город (B)
        cities = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
        sel_city = st.selectbox("📍 Город:", ["Все"] + cities)

# --- 4. ОБРАБОТКА (НОВЫЕ СВЕРХУ) ---
df_f = df_raw.iloc[::-1].copy()
if not df_raw.empty:
    if sel_org != "Все": df_f = df_f[df_f.iloc[:, 2].astype(str) == sel_org]
    if sel_city != "Все": df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_city]

# --- 5. ВЫВОД ---
st.markdown("### 🚚 Последние отгрузки")

if df_f.empty:
    st.write("Ничего не найдено")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        # Столбцы: M(12)-Дата, C(2)-Орг, B(1)-Город, K(10)-ТТН, H(7)-Состав
        date_val = str(row.iloc[12])
        org_val = str(row.iloc[2])
        city_val = str(row.iloc[1])
        ttn_val = str(row.iloc[10])
        content = str(row.iloc[7])
        
        # ЗАГОЛОВОК КАРТОЧКИ (Сжатый вид)
        label = f"{date_val}  |  {org_val}  ({city_val})"
        
        with st.expander(label):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("<span class='sub-text'>📦 Состав и Серийные номера:</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='sn-block'>{content}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<span class='sub-text'>🔗 Документы:</span>", unsafe_allow_html=True)
                if "http" in ttn_val:
                    st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-btn">ОТСЛЕДИТЬ ТТН</a>', unsafe_allow_html=True)
                else:
                    st.info(f"ТТН: {ttn_val}")
                
                # Кнопка Excel только для этой строки
                csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Скачать Excel", csv, f"ship_{idx}.csv", "text/csv", key=f"dl_{idx}")
