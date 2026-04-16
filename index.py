import streamlit as st
import pandas as pd

# --- 1. НАСТРОЙКИ СТРАНИЦЫ (СТРОГО ПЕРВАЯ СТРОКА) ---
st.set_page_config(layout="wide", page_title="LIFE PAY | Реестр", page_icon="📦")

# --- 2. БАЗА ПИН-КОДОВ (Тут ты сам решаешь, кому какой доступ) ---
PIN_DB = {
    "1234": "Все",                 # Твой админский (видит всех)
    "7788": "Автоматизация Бизнеса",
    "5544": "АРЕС-КОМПАНИ-М",
    "1122": "АТМ АЛЬЯНС СОЛЮШИНС",
    "9900": "ООО БР"
}

# Проверка авторизации (Замок)
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Реестр отгрузок | Вход</h2>", unsafe_allow_html=True)
    pin = st.text_input("Введите ваш ПИН-КОД", type="password", placeholder="****")
    if st.button("Войти"):
        if pin in PIN_DB:
            st.session_state["auth"] = True
            st.session_state["user_filter"] = PIN_DB[pin]
            st.rerun()
        else:
            st.error("Неверный ПИН-код")
    st.stop()

# --- 3. ЕСЛИ ВХОД УСПЕШЕН — ПОКАЗЫВАЕМ РЕЕСТР ---
user_filter = st.session_state["user_filter"]

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .sn-block { background: #F1F5F9; border-left: 4px solid #0052FF; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; }
    .ttn-link-btn { display: inline-block; padding: 6px 12px; background: #0052FF; color: white !important; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 12px; }
    .info-label { font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# Загрузка данных
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
    st.title("LIFE PAY")
    st.success("Доступ разрешен")
    
    # Если админ — даем выбор компании
    if user_filter == "Все":
        org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
        sel_org = st.selectbox("🏢 Выберите организацию:", ["Все"] + org_list)
    else:
        sel_org = user_filter
        st.info(f"Организация: {sel_org}")

    if st.button("Выйти"):
        st.session_state["auth"] = False
        st.rerun()

# ФИЛЬТРАЦИЯ И ВЫВОД
df_f = df_raw.iloc[::-1].copy()
if sel_org != "Все":
    df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(sel_org, na=False)]

st.header(f"📦 Реестр отгрузок: {sel_org}")

if df_f.empty:
    st.info("Данных по этой организации пока нет.")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        # M-Дата(12), C-Орг(2), B-Город(1), H-Состав(7), K-Трек(13), O-Номер(14)
        header = f"{row.iloc[12]} | {row.iloc[2]} ({row.iloc[1]})"
        with st.expander(header):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("<span class='info-label'>🛠 Состав и S/N:</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='sn-block'>{row.iloc[7]}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<span class='info-label'>📄 Номер:</span>", unsafe_allow_html=True)
                st.write(row.iloc[14])
                
                ttn_val = str(row.iloc[13])
                if "http" in ttn_val:
                    st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ ПУТЬ</a>', unsafe_allow_html=True)
                else:
                    st.code(ttn_val)
