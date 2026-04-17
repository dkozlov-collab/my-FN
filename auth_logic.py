import streamlit as st

def login_system():
    # ПИН-код: ("Название для интерфейса", "Ключевое слово для поиска в таблице")
    USERS = {
        "1121018100": ("АТМ АЛЬЯНС", "АТМ"),
        "7734595315": ("АРЕС-КОМПАНИ", "АРЕС"),
        "5321203280": ("ООО БР", "БР"),
        "9718146933": ("АВТОМАТИЗАЦИЯ", "Автомат"),
        "061219966": ("АДМИНИСТРАТОР", "Все")
    }

    if 'auth' not in st.session_state:
        st.session_state.auth = False
        st.session_state.user = ""
        st.session_state.filter = "Все"

    if st.session_state.auth:
        return True, st.session_state.user, st.session_state.filter

    st.markdown("<h2 style='text-align: center; color: #0052FF;'>LIFE PAY | ERP</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pin = st.text_input("Введите ПИН-код", type="password")
        if st.button("ВОЙТИ", use_container_width=True):
            if pin in USERS:
                st.session_state.auth = True
                st.session_state.user = USERS[pin][0]
                st.session_state.filter = USERS[pin][1]
                st.rerun()
            else:
                st.error("Неверный ПИН-код")
    
    return False, "", ""
