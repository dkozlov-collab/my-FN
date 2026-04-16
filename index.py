import streamlit as st
import pandas as pd

# 1. НАСТРОЙКИ СТРАНИЦЫ (Строго первая строка!)
st.set_page_config(layout="wide", page_title="LIFE PAY | Реестр", page_icon="🔵")

# Ссылка на твой новый значок (из твоего репозитория)
LOGO_URL = "https://raw.githubusercontent.com/dkozlov-collab/my-FN/main/1000026659.jpg"

# 2. БАЗА ПИН-КОДОВ
PIN_DB = {
    "1234": "Все",
    "7788": "Автоматизация Бизнеса",
    "5544": "АРЕС-КОМПАНИ-М",
    "1122": "АТМ АЛЬЯНС СОЛЮШИНС",
    "9900": "ООО БР"
}

# Используем новое имя сессии 'final_auth', чтобы сбросить старые входы
if "final_auth" not in st.session_state:
    st.session_state["final_auth"] = False

# --- ОКНО ВХОДА (С ПИН-КОДОМ И ЛОГО) ---
if not st.session_state["final_auth"]:
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        st.image(LOGO_URL, width=250)
        st.markdown("<h2 style='text-align: center;'>Вход в Реестр</h2>", unsafe_allow_html=True)
        
        pin = st.text_input("Введите ваш ПИН-КОД", type="password", placeholder="****")
        
        if st.button("Войти", use_container_width=True):
            if pin in PIN_DB:
                st.session_state["final_auth"] = True
                st.session_state["user_filter"] = PIN_DB[pin]
                st.rerun()
            else:
                st.error("Неверный ПИН-код!")
    st.stop()

# --- ЕСЛИ ПАРОЛЬ ВЕРЕН, ПОКАЗЫВАЕМ ВСЁ ОСТАЛЬНОЕ ---
user_filter = st.session_state["user_filter"]

# Стили для красоты (синие акценты под LIFE PAY)
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .sn-block { background: #F1F5F9; border-left: 4px solid #0052FF; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; }
    .ttn-link-btn { display: inline-block; padding: 8px 16px; background: #0052FF; color: white !important; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; }
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
    st.divider()
    if st.button("Выйти из системы"):
        st.session_state["final_auth"] = False
        st.rerun()
    
    st.divider()
    # Фильтр для админа или фиксация для клиента
    if user_filter == "Все":
        org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
        sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
    else:
        sel_org = user_filter
        st.info(f"Организация: {sel_org}")

# ФИЛЬТРАЦИЯ И ВЫВОД
df_f = df_raw.iloc[::-1].copy()
if sel_org != "Все":
    df_f = df_f[df_f.iloc[:, 2].astype(str).str.contains(sel_org, na=False)]

st.title("🚚 Реестр отгрузок")

if df_f.empty:
    st.info("Данных нет")
else:
    for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
        header = f"{row.iloc[12]} | {row.iloc[2]} ({row.iloc[1]})"
        with st.expander(header):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown("<span class='info-label'>🛠 Состав:</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='sn-block'>{row.iloc[7]}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<span class='info-label'>📄 Номер:</span>", unsafe_allow_html=True)
                st.write(row.iloc[14])
                
                ttn_val = str(row.iloc[13])
                if "http" in ttn_val:
                    st.markdown(f'<a href="{ttn_val}" target="_blank" class="ttn-link-btn">ОТСЛЕДИТЬ ПУТЬ</a>', unsafe_allow_html=True)
