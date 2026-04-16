import streamlit as st

# Связка логина из secrets и реального названия в Google Таблице
ORG_MAPPING = {
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
        st.markdown("<h2 style='text-align: center; color: #0052FF;'>🔐 LIFE PAY: Вход</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            u = st.text_input("Логин")
            p = st.text_input("Пароль", type="password")
            
            if st.button("ВОЙТИ", use_container_width=True):
                # Проверяем, есть ли такой логин в secrets.toml
                if "passwords" in st.secrets and u in st.secrets["passwords"]:
                    # Проверяем совпадение пароля
                    if st.secrets["passwords"][u] == p:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = u
                        # Берем фильтр организации для этого логина
                        st.session_state["filter"] = ORG_MAPPING.get(u, "Все")
                        st.rerun()
                    else:
                        st.error("❌ Неверный пароль")
                else:
                    st.error("❌ Пользователь не найден")
        st.stop()
    
    return True, st.session_state["user"], st.session_state["filter"]
