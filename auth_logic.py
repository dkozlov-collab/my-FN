import streamlit as st

# Связка логина и названия организации в таблице
ACCESS_CONTROL = {
    "admin": "Все",
    "biz_auto": "Автоматизация Бизнеса",
    "ares": "АРЕС-КОМПАНИ-М",
    "atm": "АТМ АЛЬЯНС СОЛЮШИНС",
    "br": "ООО БР"
}

def login_system():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Вход в LIFE PAY</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            u = st.text_input("Логин")
            p = st.text_input("Пароль", type="password")
            if st.button("ВОЙТИ", use_container_width=True):
                # Проверяем пароль из секретов
                if u in st.secrets["passwords"] and st.secrets["passwords"][u] == p:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = u
                    st.session_state["filter"] = ACCESS_CONTROL.get(u, "Все")
                    st.rerun()
                else:
                    st.error("Неверный пароль")
        st.stop()
    return True
