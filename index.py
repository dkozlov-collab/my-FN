import streamlit as st
import pandas as pd

# --- 1. СТИЛЬ LIFE PAY ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    [data-testid="stSidebar"] * { color: #1E293B !important; }
    .main-header { font-size: 30px; font-weight: 800; color: #0052FF; text-align: center; margin-bottom: 20px; }
    .card { 
        background: white; border-radius: 12px; padding: 20px; 
        margin-bottom: 15px; border-top: 4px solid #0052FF;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
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
        # Загружаем всё как есть
        s = pd.read_csv(S_URL).fillna("")
        l = pd.read_csv(L_URL).fillna("")
        # Чистим только совсем пустые строки
        s = s[s.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        l = l[l.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_all_data()

# --- 3. БЕЛАЯ ЛЕВАЯ КОНСОЛЬ ---
with st.sidebar:
    st.markdown("<h1 style='color: #0052FF; margin-bottom:0;'>LIFE PAY</h1>", unsafe_allow_html=True)
    st.markdown("<span class='badge-status'>● В РЕЙТИНГЕ</span>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("МЕНЮ УПРАВЛЕНИЯ:", ["🚚 ЛОГИСТИКА", "📦 СКЛАД", "📊 ОТГРУЗКИ"])
    st.divider()
    st.write("LIFE PAY ERP v2.0")

st.markdown(f"<div class='main-header'>LIFE PAY: {menu}</div>", unsafe_allow_html=True)

# --- 4. РАЗДЕЛ: ЛОГИСТИКА (ОБЩАЯ ТАБЛИЦА) ---
if menu == "🚚 ЛОГИСТИКА":
    st.write("### Реестр всех операций")
    if not df_l.empty:
        search_l = st.text_input("🔍 Поиск по всей таблице:")
        if search_l:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]
        st.data_editor(df_l, use_container_width=True, height=700, hide_index=True)
    else: st.warning("Таблица логистики пуста")

# --- 5. РАЗДЕЛ: СКЛАД ---
elif menu == "📦 СКЛАД":
    st.write("### Остатки на складах")
    if not df_s.empty:
        search_s = st.text_input("🔍 Быстрый поиск:")
        if search_s:
            df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
        st.data_editor(df_s, use_container_width=True, height=700, hide_index=True)
    else: st.warning("Таблица склада пуста")

# --- 6. РАЗДЕЛ: ОТГРУЗКИ (ПЛИТКА) ---
elif menu == "📊 ОТГРУЗКИ":
    if df_l.empty:
        st.info("Нет данных для формирования карточек")
    else:
        # Умные фильтры (берем столбцы по смыслу, если они есть)
        c1, c2 = st.columns(2)
        
        # Город обычно в 4-м столбце (индекс 3)
        city_col = df_l.columns[3] if len(df_l.columns) > 3 else None
        if city_col:
            with c1:
                cities = sorted([str(x) for x in df_l[city_col].unique() if str(x).strip()])
                sel_city = st.selectbox("📍 Город:", ["Все"] + cities)
        
        with c2: search_q = st.text_input("🔍 Поиск:")

        # Фильтруем
        df_f = df_l.copy()
        if city_col and sel_city != "Все":
            df_f = df_f[df_f[city_col].astype(str) == sel_city]
        if search_q:
            df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]
            # Показываем карточки
        st.write(f"Найдено: {len(df_f)}")
        grid = st.columns(3)
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            with grid[i % 3]:
                # Ищем ссылку (обычно в 11 столбце)
                ttn = str(row.iloc[10]) if len(row) > 10 else ""
                ttn_ui = f'<a href="{ttn}" target="_blank" style="color:#0052FF; font-weight:bold;">🔗 Накладная</a>' if "http" in ttn else f"📦 ТТН: {ttn}"
                
                # Получатель (столбцы 5 и 6)
                name = f"{row.iloc[4]} {row.iloc[5]}" if len(row) > 5 else "Получатель"
                
                st.markdown(f"""
                <div class="card">
                    <div style="margin-bottom:10px;">{ttn_ui}</div>
                    <div style="font-size:15px; font-weight:700;">{name}</div>
                    <div style="margin-top:10px; font-size:12px; color:gray;">
                        📍 {row.iloc[3] if len(row) > 3 else ""} | 📅 {row.iloc[0] if len(row) > 0 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📝 Детали"):
                    st.write(row) # Показываем всю строку, чтобы ничего не упустить
                    csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Excel", csv, f"r_{i}.csv", "text/csv", key=f"btn_{i}")
