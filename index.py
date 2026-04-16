    import streamlit as st
    import pandas as pd
    from auth_logic import login_system
    
    # 1. ЗАПУСКАЕМ ЗАМОК
    is_auth, user_login, user_filter = login_system()
    
    # 2. ЕСЛИ ВХОД УСПЕШЕН (обязательно ставим двоеточие в конце!)
    if is_auth:
        # ВАЖНО: Весь код ниже должен быть сдвинут ВПРАВО (на 4 пробела или 1 Tab)
        # Если он не сдвинут, Python думает, что защита к нему не относится.
        
        st.set_page_config(layout="wide", page_title="LIFE PAY | ERP")
        
        # ... тут идут твои стили, загрузка данных и карточки ...
        # УБЕДИСЬ, что каждая строчка ниже имеет отступ от края!
    # --- 1. СТИЛЬ МИНИМАЛИЗМА LIFE PAY ---
    st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")
    
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
        
        .compact-row {
            background: white; padding: 10px 15px; border-radius: 8px;
            margin-bottom: 5px; border: 1px solid #E2E8F0;
        }
        
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
    
    # --- 2. ЗАГРУЗКА ДАННЫХ ---
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
        st.divider()
        
        if not df_raw.empty:
            # Организация (Столбец C)
            org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
            sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
            
            # Город(Столбец B)
            city_list = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
            sel_city = st.selectbox("📍 Город", ["Все"] + city_list)
    
    # --- 4. СОРТИРОВКА (НОВЫЕ ВВЕРХУ) ---
    df_f = df_raw.iloc[::-1].copy()
    if not df_raw.empty:
        if sel_org != "Все": df_f = df_f[df_f.iloc[:, 2].astype(str) == sel_org]
        if sel_city != "Все": df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_city]
    
    # --- 5. ВЫВОД СПИСКА ---
    st.markdown("### 🚚 Реестр отгрузок")
    import streamlit as st
    from auth_logic import login_system
    
    # Проверка входа
    if login_system():
        st.sidebar.success(f"Вы вошли как: {st.session_state['user']}")
        
        # ТВОЙ КОД РЕЕСТРА ОТГРУЗОК ТУТ...
        # (тот, что мы писали: загрузка таблицы, фильтр по st.session_state['filter'] и т.д.)
    if df_f.empty:
        st.info("Данные не найдены")
    else:
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            # Столбцы по твоим указаниям:
            date_val = str(row.iloc[12])  # M (Дата)
            org_val = str(row.iloc[2])   # C (Организация)
            city_val = str(row.iloc[1])  # B (Город)
            ttn_val = str(row.iloc[13])   # K (Ссылка/Трек)
            content = str(row.iloc[7])   # H (Компоненты)
            move_val = str(row.iloc[14])  # O (Номер перемещения)
            
            # Заголовок компактной строки
            link_icon = "🔗" if "http" in ttn_val else "📦"
            header = f"{date_val} | {org_val} ({city_val}) {link_icon}"
            
            with st.expander(header):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("<span class='info-label'>🛠 Компоненты и серийные номера:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sn-block'>{content}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<span class='info-label'>📄 Номер перемещения (O):</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='move-number'>{move_val}</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    st.markdown("<span class='info-label'>🚚 Трек-номер (K):</span>", unsafe_allow_html=True)
                    if "http" in ttn_val:
                        st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ ПУТЬ</a>', unsafe_allow_html=True)
                    else:
                        st.code(ttn_val)
                    
                    # Кнопка Excel
                    csv_data = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Excel", csv_data, f"ship_{idx}.csv", "text/csv", key=f"dl_{idx}")
                    from auth_logic import login_system
    
    is_auth, user_login, user_filter = login_system()
    
    if is_auth:
        # Загружаем таблицу...
        df = load_data() 
        
        # ПРИМЕНЯЕМ СКРЫТЫЙ ФИЛЬТР
        if user_filter != "Все":
            # Показываем только строки этой организации (столбец C - индекс 2)
            df = df[df.iloc[:, 2].astype(str).str.contains(user_filter, na=False)]
        
        # Далее выводим красивые строки отгрузок...
