import streamlit as st
import pandas as pd
import re

# --- 1. СТИЛЬ LIFE PAY (БЕЛАЯ КОНСОЛЬ) ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

st.markdown("""
<style>
    /* Основной фон */
    .stApp { background-color: #F8FAFC; }
    
    /* ЛЕВАЯ КОНСОЛЬ - ТЕПЕРЬ БЕЛАЯ */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0; 
    }
    /* Цвет текста в меню */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { 
        color: #1E293B !important; 
        font-weight: 500;
    }
    
    /* Заголовки */
    .main-header { 
        font-size: 32px; font-weight: 900; color: #0052FF; 
        text-align: center; margin-bottom: 25px; 
    }
    
    /* КАРТОЧКИ */
    .card { 
        background: white; border-radius: 12px; padding: 20px; 
        margin-bottom: 15px; border-top: 4px solid #0052FF;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* КНОПКИ */
    .ttn-btn {
        display: inline-block; padding: 8px 16px; background-color: #0052FF;
        color: white !important; border-radius: 6px; text-decoration: none;
        font-weight: bold; font-size: 13px;
    }
    .badge-status { 
        background-color: #DCFCE7; color: #166534; 
        padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; 
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_all_data():
    try:
        s = pd.read_csv(S_URL).fillna(0)
        l = pd.read_csv(L_URL).fillna("")
        s = s[~s.iloc[:, 1].astype(str).str.strip().isin(["0", "0.0", "", "СП", "Партнер"])]
        if not l.empty:
            l.iloc[:, 0] = pd.to_datetime(l.iloc[:, 0], errors='coerce')
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_all_data()

# --- 3. БЕЛАЯ ЛЕВАЯ КОНСОЛЬ ---
with st.sidebar:
    st.markdown("<h1 style='color: #0052FF;'>LIFE PAY</h1>", unsafe_allow_html=True)
    st.markdown("<span class='badge-status'>● В РЕЙТИНГЕ</span>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("МЕНЮ УПРАВЛЕНИЯ:", ["🚚 ЛОГИСТИКА", "📦 СКЛАД", "📊 ОТГРУЗКИ"])
    st.divider()
    st.write("LIFE PAY ERP v2.0")
    st.write("© 2026 Все права защищены")

st.markdown(f"<div class='main-header'>LIFE PAY: {menu}</div>", unsafe_allow_html=True)

# --- 4. РАЗДЕЛ: ЛОГИСТИКА ---
if menu == "🚚 ЛОГИСТИКА":
    st.subheader("Реестр логистических операций")
    st.data_editor(df_l, use_container_width=True, height=600, hide_index=True)

# --- 5. РАЗДЕЛ: СКЛАД ---
elif menu == "📦 СКЛАД":
    st.subheader("Текущие остатки на складах")
    search = st.text_input("🔍 Быстрый поиск:")
    if search:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.data_editor(df_s, use_container_width=True, height=600, hide_index=True)

# --- 6. РАЗДЕЛ: ОТГРУЗКИ (ПЛИТКА) ---
elif menu == "📊 ОТГРУЗКИ":
    if df_l.empty:
        st.info("Данные отсутствуют")
    else:
        # Панель управления
        f1, f2 = st.columns(2)
        with f1:
            cities = sorted([str(x) for x in df_l.iloc[:, 3].unique() if str(x).strip()])
            sel_city = st.selectbox("📍 Город отправки:", ["Все города"] + cities)
        with f2:
            search_l = st.text_input("🔍 Поиск по ТТН / Получателю:")

        df_f = df_l.copy()
        if sel_city != "Все города":
            df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]
        if search_l:
            df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
            st.write(f"Найдено: {len(df_f)} отгрузок")
        
        # Карточки
        grid = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with grid[i % 3]:
                # Ссылка на ТТН
                ttn = str(row.iloc[10]) if len(row) > 10 else ""
                btn_ui = f'<a href="{ttn}" target="_blank" class="ttn-btn">🔗 Накладная</a>' if "http" in ttn else f"📦 ТТН: {ttn}"
                
                # Получатель
                rec = f"{row.iloc[4]} {row.iloc[5]}" if len(row) > 5 else "Не указан"

                st.markdown(f"""
                <div class="card">
                    <div style="margin-bottom:12px;">{btn_ui}</div>
                    <div style="font-size:16px; font-weight:700; color:#1E293B;">{rec}</div>
                    <div style="margin-top:12px;">
                        <span style="background:#F1F5F9; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold;">📍 {row.iloc[3]}</span>
                        <span style="font-size:11px; color:#64748B; margin-left:10px;">
                            📅 {row.iloc[0].strftime('%d.%m.%Y') if pd.notnull(row.iloc[0]) else ''}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📝 Состав заказа"):
                    st.write(f"Оборудование: {row.iloc[7] if len(row) > 7 else '---'}")
                    st.write(f"Статус: В рейтинге")
                    excel = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Excel", excel, f"ship_{i}.csv", "text/csv", key=f"btn_{i}")
