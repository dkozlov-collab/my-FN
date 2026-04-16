import streamlit as st
import pandas as pd
from auth_logic import login_system

# 1. НАСТРОЙКИ СТРАНИЦЫ (Самый верх)
st.set_page_config(page_title="RBS GLOBAL ERP", page_icon="💎", layout="wide")

# 2. АВТОРИЗАЦИЯ
auth_status, user_login, user_filter = login_system()

if auth_status:
    # --- ФУНКЦИЯ ЗАГРУЗКИ ДАННЫХ ---
    @st.cache_data(ttl=60)
    def load_data():
        # Ссылка на твою таблицу (проверь, чтобы она была верной)
        sheet_id = "1D7f_eI4E8W0E9rM0_G-n4vY9vU7v5y1y" 
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        try:
            return pd.read_csv(url)
        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")
            return pd.DataFrame()

    # --- 4. ЗАГРУЗКА ДАННЫХ ---
    df_raw = load_data()

    # --- 5. БОКОВАЯ ПАНЕЛЬ (ТОЛЬКО ФИЛЬТРЫ) ---
    with st.sidebar:
        st.markdown("<h2 style='color:#0052FF'>РЕЕСТР ОТГРУЗОК</h2>", unsafe_allow_html=True)
        st.write(f"👤 Пользователь: {user_login}")
        st.divider()

        if not df_raw.empty:
            # Получаем список организаций
            org_list = sorted([str(x) for x in df_raw.iloc[:, 2].unique() if str(x).strip()])
            
            # Фильтр организации: партнер видит только себя, админ - всех
            if user_filter != "Все":
                user_orgs = [org for org in org_list if user_filter.lower() in org.lower()]
                sel_org = st.selectbox("🏢 Организация:", user_orgs)
            else:
                sel_org = st.selectbox("🏢 Организация:", ["Все"] + org_list)
            
            # Фильтр города
            city_list = sorted([str(x) for x in df_raw.iloc[:, 1].unique() if str(x).strip()])
            sel_city = st.selectbox("📍 Город:", ["Все"] + city_list)
        
        st.divider()
        if st.button("🔄 Обновить данные"):
            st.cache_data.clear()
            st.rerun()

    # --- 6. ГЛАВНАЯ СТРАНИЦА (РЕЕСТР) ---
    st.markdown("## 🚚 Список отгрузок")

    if not df_raw.empty:
        # Копируем данные для фильтрации
        df_f = df_raw.iloc[::-1].copy()

        # Применяем фильтры из боковой панели
        if sel_org != "Все":
            df_f = df_f[df_f[df_f.columns[2]].astype(str) == sel_org]
        if sel_city != "Все":
            df_f = df_f[df_f[df_f.columns[1]].astype(str) == sel_city]

        if df_f.empty:
            st.info("Данные по выбранным фильтрам не найдены")
        else:
            # Вывод карточек отгрузок
            for idx, row in df_f.reset_index(drop=True).iterrows():
                date_val = str(row.iloc[12])
                org_val = str(row.iloc[2])
                city_val = str(row.iloc[1])
                
                header = f"{date_val} | {org_val} ({city_val})"
                
                with st.expander(header):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("📦 ОБОРУДОВАНИЕ:")
                        content = str(row.iloc[7]).split(',')[0].strip()
                        st.info(content)
                    
                    with col2:
                        move_val = str(row.iloc[14])
                        edo_val = str(row.iloc[15])
                        
                        st.markdown(f"📄 Номер перемещения: {move_val}")
                        
                        # Цвет статуса ЭДО
                        color = "#28a745" if "Подписано" in edo_val else "#ff4b4b" if "Направлено" in edo_val else "#31333F"
                        st.markdown(f"📝 ЭДО: <span style='color:{color}; font-weight:bold;'>{edo_val}</span>", unsafe_allow_html=True)

    else:
        st.warning("Таблица пуста или не загрузилась.")

else:
    # Если не авторизован, login_system сама покажет форму входа
    st.stop()
