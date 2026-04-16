import streamlit as st
import pandas as pd

# 1. НАСТРОЙКИ СТРАНИЦЫ
st.set_page_config(layout="wide", page_title="LIFE PAY | Реестр", page_icon="🔵")

# ЛОГОТИП
LOGO_URL = "https://raw.githubusercontent.com/dkozlov-collab/my-FN/main/1000026659.jpg"

# 2. БАЗА ПИН-КОДОВ
PIN_DB = {
    "1234": "Все",
    "7788": "Автоматизация Бизнеса",
    "5544": "АРЕС-КОМПАНИ-М",
    "1122": "АТМ АЛЬЯНС СОЛЮШИНС",
    "9900": "ООО БР"
}

# Ключ сессии (изменил на 'v3_auth', чтобы сбросить старые входы)
if "v3_auth" not in st.session_state:
    st.session_state["v3_auth"] = False

# --- БЛОК ВХОДА ---
if not st.session_state["v3_auth"]:
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        try:
            st.image(LOGO_URL, width=250)
        except:
            st.write("### LIFE PAY")
        
        st.markdown("<h3 style='text-align: center;'>Вход в Реестр</h3>", unsafe_allow_html=True)
        
        user_pin = st.text_input("Введите ПИН-КОД", type="password", label_visibility="collapsed")
        
        if st.button("ВОЙТИ", use_container_width=True):
            if user_pin in PIN_DB:
                st.session_state["v3_auth"] = True
                st.session_state["user_filter"] = PIN_DB[user_pin]
                st.rerun()
            else:
                st.error("Неверный код доступа")
    st.stop()

# --- ОСНОВНОЙ КОНТЕНТ (ПОСЛЕ ВХОДА) ---
user_filter = st.session_state["user_filter"]

# Стили для синего акцента и шрифтов
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .sn-block { 
        background: #F1F5F9; 
        border-left: 4px solid #0052FF; 
        padding: 15px; 
        border-radius: 8px; 
        font-family: monospace; 
        font-size: 14px; 
        white-space: pre-wrap;
    }
    .info-label { font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ЗАГРУЗКА ДАННЫХ
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(L_URL).fillna("")
        return df[df.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
    except: return pd.DataFrame()

df_raw = load_data()

# БОКОВАЯ ПАНЕЛЬ
with st.sidebar:
    st.image(LOGO_URL, width=150)
    st.success(f"Доступ: {user_filter}")
    if st.button("Выйти"):
        st.session_state["v3_auth"] = False
        st.rerun()
    
    st.divider()
    # Фильтр для админа
    if user_filter == "Все":
        org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
        sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
    else:
        sel_org = user_filter

# ВЫВОД РЕЕСТРА
st.title("🚚 Реестр отгрузок")

df_f = df_raw.iloc[::-1].copy()
if sel_org != "Все":
    df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(sel_org, na=False)]

if df_f.empty:
    st.info("Данных пока нет")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        # Заголовок карточки
        header_text = f"{row.iloc[2]} — {row.iloc[1]}"
        
        with st.expander(header_text):
            # 1. Дата отправления (автоматически из столбца M)
            st.markdown(f"📅 Дата отправления: {row.iloc[12]}")
            
            # 2. Оборудование и описание
            st.markdown("<span class='info-label'>📦 Оборудование и описание:</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='sn-block'>{row.iloc[7]}</div>", unsafe_allow_html=True)
            
            # 3. Кнопка скачивания деталей
            csv_data = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Сохранить детали", csv_data, f"ship_{idx}.csv", "text/csv", key=f"dl_{idx}")
