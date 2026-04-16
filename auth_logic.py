import streamlit as st

def login_system():
    # 1. Список ПИН-кодов и доступов
    # Формат: "ПИН-КОД": ("Имя пользователя", "Фильтр организации")
    USERS = {
        "1121018100": ("Менеджер 1", "ООО АТМ АЛЬЯНС СОЛЮШИНС"),  # Только эта орг.
        "7734595315": ("Менеджер 2", "ООО АРЕС-КОМПАНИ-М"),      # Только эта орг.
        "5321203280": ("Менеджер 3", "ООО БР"),                  # Только эта орг.
        "9718146933": ("Менеджер 4", "Автоматизация Бизнеса"),    # Только эта орг.
        "9701010050": ("Администратор", "Все")                   # Видит ВСЕ организации
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
