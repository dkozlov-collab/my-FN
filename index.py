import streamlit as st
import pandas as pd
from auth_logic import login_system

# 1. НАСТРОЙКИ СТРАНИЦЫ (Должны быть строго первыми!)
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

# 2. ПРОВЕРКА ПИН-КОДА
is_auth, user_login, user_filter = login_system()

if is_auth:
    # --- СТИЛИ ОФОРМЛЕНИЯ ---
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
        .sn-block {
            background: #F1F5F9; border-left: 4px solid #0052FF;
            padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px;
            white-space: pre-wrap; color: #1E293B;
        }
        .ttn-link-btn {
            display: inline-block; padding: 6px 12px; background: #0052FF;
            color: white !important; border-radius: 6px; text-decoration: none;
            font-weight: 700; font-size: 12px; margin-top: 10px;
        }
        .info-label { font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; }
        .move-number { color: #0052FF; font-weight: 800; font-size: 15px; }
    </style>
    """, unsafe_allow_html=True)

    # --- ЗАГРУЗКА ДАННЫХ ---
    L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"
    
    @st.cache_data(ttl=5)
    def load_data():
        try:
            df = pd.read_csv(L_URL).fillna("")
            return df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        except: return pd.DataFrame()
    
    df_raw = load_data()

    # --- БОКОВАЯ ПАНЕЛЬ И ФИЛЬТРЫ ---
    with st.sidebar:
        st.markdown("<h2 style='color:#0052FF'>LIFE PAY</h2>", unsafe_allow_html=True)
        st.success(f"Вход выполнен")
        st.divider()
        
        # Если зашел АДМИН (user_filter == "Все")
        if user_filter == "Все":
            org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
            sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
        else:
            # Если партнер - фиксируем его компанию
            sel_org = user_filter
            st.info(f"Организация: {sel_org}")
            
        city_list = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
        sel_city = st.selectbox("📍 Город", ["Все"] + city_list)

        if st.button("Выйти"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- ОБРАБОТКА И ВЫВОД РЕЕСТРА ---
    df_f = df_raw.iloc[::-1].copy() # Новые сверху
    
    if not df_f.empty:
        if sel_org != "Все": 
            df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(sel_org, na=False)]
        if sel_city != "Все": 
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_city]

    st.markdown(f"### 🚚 Реестр отгрузок: {sel_org}")

    if df_f.empty:
        st.info("Данные не найдены")
    else:
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            # Вытягиваем данные по столбцам
            date_val = str(row.iloc[12])
            org_name = str(row.iloc[2])
            city_val = str(row.iloc[1])
            content = str(row.iloc[7])
            ttn_val = str(row.iloc[13])
            move_val = str(row.iloc[14])

            header = f"{date_val} | {org_name} ({city_val})"
            
            with st.expander(header):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("<span class='info-label'>🛠 Компоненты:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sn-block'>{content}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<span class='info-label'>📄 Номер перемещения:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='move-number'>{move_val}</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    st.markdown("<span class='info-label'>🚚 Трек-номер:</span>", unsafe_allow_html=True)
                    if "http" in ttn_val:
                        st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ</a>', unsafe_allow_html=True)
                    else:
                        st.code(ttn_val)
                    
