import streamlit as st
import pandas as pd

# --- 1. СТИЛЬ LIFE PAY (БЕЛАЯ КОНСОЛЬ) ---
st.set_page_config(layout="wide", page_title="LIFE PAY | ERP", page_icon="🔵")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    [data-testid="stSidebar"] * { color: #1E293B !important; }
    .main-header { font-size: 28px; font-weight: 800; color: #0052FF; margin-bottom: 20px; }
    
    /* СТИЛЬ СТРОКИ-КАРТОЧКИ (ВМЕСТО КУБИКОВ) */
    .shipping-row {
        background: white; border-radius: 8px; padding: 15px;
        margin-bottom: 10px; border-left: 5px solid #0052FF;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .row-info { flex: 2; font-size: 14px; }
    .row-details { flex: 3; font-size: 13px; color: #475569; border-left: 1px solid #E2E8F0; padding-left: 15px; margin-left: 15px; }
    .btn-block { flex: 1; text-align: right; }
    
    .ttn-link { color: #0052FF; font-weight: bold; text-decoration: none; font-size: 15px; }
    .badge-status { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ (БЕЗЛИМИТ 80 СТ) ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

@st.cache_data(ttl=5)
def load_all_data():
    try:
        s = pd.read_csv(S_URL).fillna("")
        l = pd.read_csv(L_URL).fillna("")
        # Чистим пустые строки
        s = s[s.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        l = l[l.apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_all_data()

# --- 3. БЕЛАЯ ЛЕВАЯ КОНСОЛЬ (ФИЛЬТРЫ) ---
with st.sidebar:
    st.markdown("<h1 style='color: #0052FF; margin-bottom:0;'>LIFE PAY</h1>", unsafe_allow_html=True)
    st.markdown("<span class='badge-status'>● В РЕЙТИНГЕ</span>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio("МЕНЮ:", ["🚚 ЛОГИСТИКА", "📦 СКЛАД", "📊 ОТГРУЗКИ"])
    st.divider()
    
    # ГЛОБАЛЬНЫЕ ФИЛЬТРЫ
    st.write("🔍 ФИЛЬТРАЦИЯ ПОИСКА")
    
    # Фильтр по Партнеру (из логистики, обычно 2 столбец)
    partners = sorted([str(x) for x in df_l.iloc[:, 1].unique() if str(x).strip()])
    sel_partner = st.selectbox("🤝 Партнер:", ["Все"] + partners)
    
    # Фильтр по Организации (обычно 6 столбец / индекс 5)
    orgs = sorted([str(x) for x in df_l.iloc[:, 5].unique() if str(x).strip() and str(x) != "0"])
    sel_org = st.selectbox("🏢 Организация:", ["Все"] + orgs)

    st.divider()
    st.write("LIFE PAY ERP v3.0")

# --- 4. ПРИМЕНЕНИЕ ФИЛЬТРОВ К ДАННЫМ ---
if sel_partner != "Все":
    df_l = df_l[df_l.iloc[:, 1].astype(str) == sel_partner]
if sel_org != "Все":
    df_l = df_l[df_l.iloc[:, 5].astype(str) == sel_org]

st.markdown(f"<div class='main-header'>LIFE PAY: {menu}</div>", unsafe_allow_html=True)

# --- 5. РАЗДЕЛ: СКЛАД (80 СТОЛБЦОВ + СОРТИРОВКА) ---
if menu == "📦 СКЛАД":
    st.write(f"### Складской учет (Всего колонок: {df_s.shape[1]})")
    search_s = st.text_input("🔍 Быстрый поиск по складу:")
    if search_s:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    # Выводим таблицу с сортировкой (нажми на заголовок)
    st.data_editor(df_s, use_container_width=True, height=750, hide_index=True)

# --- 6. РАЗДЕЛ: ЛОГИСТИКА ---
elif menu == "🚚 ЛОГИСТИКА":
    st.write("### Общий реестр логистики")
    st.data_editor(df_l, use_container_width=True, height=700, hide_index=True)
    # --- 7. РАЗДЕЛ: ОТГРУЗКИ (ЛИНЕЙНЫЙ ВИД) ---
elif menu == "📊 ОТГРУЗКИ":
    if df_l.empty:
        st.info("Нет данных по заданным фильтрам")
    else:
        # Новые сверху
        df_f = df_l.iloc[::-1].copy()
        
        # Фильтр по городу в самой вкладке
        cities = sorted([str(x) for x in df_l.iloc[:, 3].unique() if str(x).strip()])
        sel_city = st.selectbox("📍 Город отправки:", ["Все"] + cities)
        if sel_city != "Все":
            df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]

        st.write(f"Найдено: {len(df_f)} отгрузок")

        # ВЫВОД СТРОКАМИ
        for i, (idx, row) in enumerate(df_f.reset_index(drop=True).iterrows()):
            ttn = str(row.iloc[10]) if len(row) > 10 else "---"
            date_val = str(row.iloc[0])[:10]
            rec_name = f"{row.iloc[4]} | {row.iloc[5]}" # Получатель + Организация
            
            # Рендерим строку
            st.markdown(f"""
            <div class="shipping-row">
                <div class="row-info">
                    <span style="color:gray; font-weight:bold;">{date_val}</span><br>
                    <a href="{ttn if 'http' in ttn else '#'}" target="_blank" class="ttn-link">
                        {'🔗 Накладная ТТН' if 'http' in ttn else '📦 ТТН: '+ttn}
                    </a><br>
                    <b>{rec_name}</b>
                </div>
                <div class="row-details">
                    <b>📍 {row.iloc[3]}</b><br>
                    Состав: {str(row.iloc[7])[:150]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопка Excel и полные данные под каждой строкой
            with st.expander("📂 Посмотреть полный состав и скачать Excel"):
                st.write(row)
                csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Скачать Excel отгрузки", csv, f"r_{i}.csv", "text/csv", key=f"btn_{i}")
