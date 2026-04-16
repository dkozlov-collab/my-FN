import streamlit as st
import pandas as pd
from auth_logic import login_system

# --- 1. ПРОВЕРКА АВТОРИЗАЦИИ (ЗАМОК) ---
# Эта функция отрисовывает окно ввода ПИН-кода
is_auth, user_login, user_filter = login_system()

# --- 2. ВЕСЬ КОД НИЖЕ ЗАПУСКАЕТСЯ ТОЛЬКО ПОСЛЕ ВВОДА ПИН-КОДА ---
if is_auth:
    # Настройка страницы
    st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")
    
    # --- 3. СТИЛЬ (КАК НА СКРИНШОТАХ) ---
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
        
        /* Стиль заголовка */
        h3 { font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }

        /* Карточка отгрузки (Expander) */
        [data-testid="stExpander"] { 
            background: white; border-radius: 8px; border: 1px solid #E2E8F0; 
            margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); 
        }
        
        /* Блок серийников (левая колонка) */
        .sn-block {
            background: #F1F5F9; border-left: 4px solid #0052FF;
            padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px;
            white-space: pre-wrap; color: #1E293B; min-height: 110px;
        }

        /* Подписи и Номер перемещения */
        .info-label { font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 4px; }
        .move-number { color: #0052FF; font-weight: 800; font-size: 15px; margin-bottom: 15px; }

        /* Синяя кнопка ТРЕК-НОМЕРА (как на скрине) */
        .ttn-link-btn {
            display: block; width: 100%; text-align: center; padding: 10px; 
            background: #0052FF; color: white !important; border-radius: 8px; 
            text-decoration: none; font-weight: 700; font-size: 13px; margin-top: 5px;
        }
        .ttn-link-btn:hover { background: #0042CC; }

        /* Кнопка Excel */
        [data-testid="stDownloadButton"] > button {
            width: 100%; background-color: #FFFFFF; color: #4A5568; 
            border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 4. ЗАГРУЗКА ДАННЫХ ---
    L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"
    
    @st.cache_data(ttl=5)
    def load_data():
        try:
            df = pd.read_csv(L_URL).fillna("")
            return df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        except: 
            return pd.DataFrame()

    df_raw = load_data()

   # ПРИМЕНЯЕМ СКРЫТЫЙ ФИЛЬТР (ИЗ ПИН-КОДА)
    if not df_raw.empty and user_filter != "Все":
        # Делаем поиск по части слова, не обращая внимания на большие/маленькие буквы
        mask = df_raw.iloc[:, 2].astype(str).str.contains(user_filter, case=False, na=False)
        df_raw = df_raw[mask]
    # --- 6. БОКОВАЯ ПАНЕЛЬ ---
    with st.sidebar:
        st.markdown("<h2 style='color:#0052FF'>LIFE PAY</h2>", unsafe_allow_html=True)
        st.write(f"👤 Пользователь: {user_login}")
        st.divider()
        
        if not df_raw.empty:
            # Фильтр Организация
            org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
            sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
            
            # Фильтр Город
            city_list = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
            sel_city = st.selectbox("📍 Город", ["Все"] + city_list)

    # --- 7. ПОДГОТОВКА СПИСКА (СОРТИРОВКА) ---
    df_f = df_raw.iloc[::-1].copy() # Новые сверху
    if not df_raw.empty:
        if sel_org != "Все": 
            df_f = df_f[df_f.iloc[:, 2].astype(str) == sel_org]
        if sel_city != "Все": 
            df_f = df_f[df_f.iloc[:, 1].astype(str) == sel_city]
            # --- 8. ВЫВОД РЕЕСТРА ---
    st.markdown("### 🚚 Реестр отгрузок")
    
    if df_f.empty:
        st.info("Данные не найдены")
    else:
        for idx, row in df_f.reset_index(drop=True).iterrows():
            # Назначение столбцов:
            # B=1(Город), C=2(Орг), H=7(Состав), M=12(Дата), N=13(Трек), O=14(Перемещение)
            date_val = str(row.iloc[12])  
            org_val  = str(row.iloc[2])   
            city_val = str(row.iloc[1])   
        ttn_val = str(row.iloc[13])  # ТУТ ИСПРАВИЛ НА iloc
        raw_content = str(row.iloc[7])
        content = raw_content.split(',')[0].strip() # ТУТ ДОБАВИЛ ОЧИСТКУ
        move_val = str(row.iloc[14])
        raw_content.split(',')[0].strip()
            move_val = str(row.iloc[14])  

            # Иконка в заголовке
            icon = "🔗" if "http" in ttn_val else "📦"
            header = f"{date_val} | {org_val} ({city_val}) {icon}"
            
            with st.expander(header):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("<span class='info-label'>🛠 Компоненты и серийные номера:</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sn-block'>{content}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<span class='info-label'>📄 Номер перемещения (O):</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='move-number'>{move_val}</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    st.markdown("<span class='info-label'>🚚 Трек-номер (N):</span>", unsafe_allow_html=True)
                    
                    # Логика трек-номера: если ссылка - кнопка, если текст - код
                    if "http" in ttn_val:
                        st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ ПУТЬ</a>', unsafe_allow_html=True)
                    elif ttn_val.strip():
                        st.code(ttn_val)
                    else:
                        st.write("Не указан")
                    
                    # Кнопка Excel для конкретной строки
                    csv_data = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Excel", csv_data, f"ship_{idx}.csv", "text/csv", key=f"dl_{idx}")

else:
    # Пока ПИН-код не введен, выполнение кода останавливается здесь
    st.stop()
import streamlit as st

def login_system():
    # 1. Список ПИН-кодов и доступов
    # Формат: "ПИН-КОД": ("Имя пользователя", "Фильтр организации")
    USERS = {
        "1111": ("Менеджер 1", "ООО АТМ АЛЬЯНС СОЛЮШИНС"),  # Только эта орг.
        "2222": ("Менеджер 2", "ООО АРЕС-КОМПАНИ-М"),      # Только эта орг.
        "3333": ("Менеджер 3", "ООО БР"),                  # Только эта орг.
        "4444": ("Менеджер 4", "Автоматизация Бизнеса"),    # Только эта орг.
        "0000": ("Администратор", "Все")                   # Видит ВСЕ организации
    }

    # Инициализация состояния сессии
    if 'auth' not in st.session_state:
        st.session_state.auth = False
        st.session_state.user = ""
        st.session_state.filter = "Все"

    # Если уже авторизован
    if st.session_state.auth:
        return True, st.session_state.user, st.session_state.filter

    # Окно входа (Интерьер как на LIFE PAY)
    st.markdown("<h2 style='text-align: center; color: #0052FF;'>LIFE PAY | Вход</h2>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            pin = st.text_input("Введите ПИН-код", type="password", help="4 цифры")
            if st.button("Войти", use_container_width=True):
                if pin in USERS:
                    st.session_state.auth = True
                    st.session_state.user = USERS[pin][0]
                    st.session_state.filter = USERS[pin][1]
                    st.rerun()
                else:
                    st.error("Неверный ПИН-код")
    
    return False, "", ""
