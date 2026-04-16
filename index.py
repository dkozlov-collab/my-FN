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
        margin-bottom: 15px; border-top: 5px solid #0052FF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .badge-new { background-color: #0052FF; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    .badge-status { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ (БЕЗ ОГРАНИЧЕНИЙ ПО КОЛОНКАМ) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_all_data():
    try:
        # Читаем все колонки (без ограничений)
        s = pd.read_csv(S_URL).fillna("")
        l = pd.read_csv(L_URL).fillna("")
        # Чистим пустые строки
        s = s[s.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        l = l[l.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_all_data()

# --- 3. МЕНЮ ---
with st.sidebar:
    st.markdown("<h1 style='color: #0052FF; margin-bottom:0;'>LIFE PAY</h1>", unsafe_allow_html=True)
    st.markdown("<span class='badge-status'>● В РЕЙТИНГЕ</span>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("МЕНЮ УПРАВЛЕНИЯ:", ["📦 СКЛАД", "🚚 ЛОГИСТИКА", "📊 ОТГРУЗКИ"])
    st.divider()
    st.write("v 2.2 | Full Scan")

st.markdown(f"<div class='main-header'>LIFE PAY: {menu}</div>", unsafe_allow_html=True)

# --- 4. СКЛАД (ГЛУБОКИЙ СКАН ДО 80+ СТОЛБЦОВ) ---
if menu == "📦 СКЛАД":
    if not df_s.empty:
        st.write(f"### Реестр остатков (Доступно колонок: {df_s.shape[1]})")
        search_s = st.text_input("🔍 Поиск по всей глубине склада (серийник, модель, город):")
        
        if search_s:
            df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
        
        # Вывод таблицы с горизонтальным скроллом
        st.data_editor(df_s, use_container_width=True, height=750, hide_index=True)
    else: 
        st.warning("Данные склада не подгрузились. Проверьте доступ к таблице.")

# --- 5. ЛОГИСТИКА ---
elif menu == "🚚 ЛОГИСТИКА":
    if not df_l.empty:
        st.write("### Общий реестр операций")
        st.data_editor(df_l, use_container_width=True, height=700, hide_index=True)
    else: 
        st.warning("Данные логистики пусты")

# --- 6. ОТГРУЗКИ ---
elif menu == "📊 ОТГРУЗКИ":
    if df_l.empty:
        st.info("Нет данных")
    else:
        # Самые новые сверху
        df_f = df_l.iloc[::-1].copy() 

        c1, c2 = st.columns(2)
        # Город (обычно 4-я колонка)
        if len(df_l.columns) > 3:
            city_col = df_l.columns[3]
            with c1:
                cities = sorted([str(x) for x in df_l[city_col].unique() if str(x).strip()])
                sel_city = st.selectbox("📍 Город:", ["Все"] + cities)
                if sel_city != "Все":
                    df_f = df_f[df_f[city_col].astype(str) == sel_city]
        
        with c2:
            search_q = st.text_input("🔍 Быстрый поиск:")
            if search_q:
                df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]
                st.write(f"Найдено: {len(df_f)} (Сортировка: Сначала новые)")
        
        grid = st.columns(3)
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            with grid[i % 3]:
                # Ссылка на ТТН (обычно 11-я колонка)
                ttn = str(row.iloc[10]) if len(row) > 10 else "---"
                ttn_ui = f'<a href="{ttn}" target="_blank" style="color:#0052FF; font-weight:bold;">🔗 Накладная</a>' if "http" in ttn else f"📦 ТТН: {ttn[:20]}..."
                
                # Получатель
                name = f"{row.iloc[4]} {row.iloc[5]}" if len(row) > 5 else "Получатель"
                new_tag = '<div class="badge-new">NEW</div>' if i == 0 else ""

                st.markdown(f"""
                <div class="card">
                    {new_tag}
                    <div style="margin-bottom:10px;">{ttn_ui}</div>
                    <div style="font-size:15px; font-weight:700; color:#1E293B;">{name}</div>
                    <div style="margin-top:10px; font-size:11px; color:#64748B;">
                        📍 {row.iloc[3] if len(row) > 3 else "---"} | 📅 {row.iloc[0] if len(row) > 0 else "---"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📝 Состав и экспорт"):
                    st.write(row) # Выводит всю строку данных
                    csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Excel этой строки", csv, f"row_{i}.csv", "text/csv", key=f"dl_{i}")
