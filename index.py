import streamlit as st
import pandas as pd
from auth_logic import login_system  # Твой замок

# 1. ЗАПУСКАЕМ ПРОВЕРКУ (Окно входа)
is_auth, user_login, user_filter = login_system()

# 2. ВСЁ ЧТО НИЖЕ — ПОД ЗАМКОМ
if is_auth:
    # --- НАСТРОЙКИ СТРАНИЦЫ ---
    st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")
    
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

    # --- БОКОВАЯ ПАНЕЛЬ ---
    with st.sidebar:
        st.markdown("<h2 style='color:#0052FF'>LIFE PAY</h2>", unsafe_allow_html=True)
        st.success(f"Пользователь: {user_login}")
        st.divider()
        
        # ЛОГИКА ФИЛЬТРА: Админ выбирает всех, партнер видит только своё
        if user_filter == "Все":
            org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
            sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
        else:
            sel_org = user_filter
            st.info(f"Доступ только к: {sel_org}")

        if st.button("Выйти"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- ОБРАБОТКА ДАННЫХ ---
    df_f = df_raw.iloc[::-1].copy() # Новые сверху
    
    # Применяем фильтр организации (Столбец C - индекс 2)
    if sel_org != "Все":
        df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(sel_org, na=False)]

    # --- ВЫВОД РЕЕСТРА ---
    st.markdown(f"### 🚚 Реестр отгрузок: {sel_org}")

    if df_f.empty:
        st.info("Данные не найдены")
    else:
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            # Столбцы: M(12)-Дата, C(2)-Орг, B(1)-Город, K(13)-Трек, H(7)-Состав, O(14)-Перемещение
            header = f"{row.iloc[12]} | {row.iloc[2]} ({row.iloc[1]})"
            
            with st.expander(header):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("<span class='info-label'>🛠 Состав:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sn-block'>{row.iloc[7]}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<span class='info-label'>📄 Перемещение:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='move-number'>{row.iloc[14]}</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    ttn_val = str(row.iloc[13])
                    if "http" in ttn_val:
                        st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ</a>', unsafe_allow_html=True)
                    else:
                        st.code(ttn_val)
