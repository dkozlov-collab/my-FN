import streamlit as st
import pandas as pd

# 1. НАСТРОЙКИ (СТРОГО ПЕРВЫЕ)
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

# 2. ТВОЙ НОВЫЙ ЗНАЧОК
LOGO_URL = "https://raw.githubusercontent.com/dkozlov-collab/my-FN/main/1000026659.jpg"

# 3. ПИН-КОДЫ
PIN_DB = {
    "1234": "Все",
    "7788": "Автоматизация Бизнеса",
    "5544": "АРЕС-КОМПАНИ-М",
    "1122": "АТМ АЛЬЯНС СОЛЮШИНС",
    "9900": "ООО БР"
}

# МЕНЯЕМ КЛЮЧ НА 'ultra_secure_login' — это сбросит кэш у всех!
if "ultra_secure_login" not in st.session_state:
    st.session_state["ultra_secure_login"] = False

# --- ОКНО ВХОДА ---
if not st.session_state["ultra_secure_login"]:
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        try:
            st.image(LOGO_URL, width=250)
        except:
            st.write("### LIFE PAY")
        
        st.markdown("<h3 style='text-align: center;'>Введите ПИН-КОД</h3>", unsafe_allow_html=True)
        
        # Поле ввода
        user_pin = st.text_input("PIN", type="password", label_visibility="collapsed")
        
        if st.button("ВОЙТИ", use_container_width=True):
            if user_pin in PIN_DB:
                st.session_state["ultra_secure_login"] = True
                st.session_state["user_filter"] = PIN_DB[user_pin]
                st.rerun()
            else:
                st.error("Неверный ПИН-код!")
    st.stop() # Дальше код не пойдет, пока не введешь ПИН

# --- ВСЁ, ЧТО НИЖЕ, ВИДНО ТОЛЬКО ПОСЛЕ ПИН-КОДА ---
user_filter = st.session_state["user_filter"]

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .sn-block { background: #F1F5F9; border-left: 4px solid #0052FF; padding: 15px; border-radius: 8px; font-family: monospace; }
    .ttn-btn { display: inline-block; padding: 8px 16px; background: #0052FF; color: white !important; border-radius: 6px; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ЗАГРУЗКА
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
        st.session_state["ultra_secure_login"] = False
        st.rerun()

# ФИЛЬТР И ВЫВОД
df_f = df_raw.iloc[::-1].copy()
if user_filter != "Все":
    df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(user_filter, na=False)]

st.title("🚚 Реестр отгрузок")

if df_f.empty:
    st.info("Данных нет")
else:
    for i, row in df_f.iterrows():
        with st.expander(f"{row.iloc[12]} | {row.iloc[2]}"):
            st.markdown(f"<div class='sn-block'>{row.iloc[7]}</div>", unsafe_allow_html=True)
            st.write(f"Перемещение: {row.iloc[14]}")
