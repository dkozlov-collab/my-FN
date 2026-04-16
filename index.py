import streamlit as st
import pandas as pd
import re

# --- 1. СТИЛЬ LIFE PAY ---
st.set_page_config(layout="wide", page_title="LIFE PAY | Система управления", page_icon="🔵")

st.markdown("""
<style>
    .stApp { background-color: #F0F4F8; }
    /* Синий брендовый цвет LIFE PAY */
    [data-testid="stSidebar"] { background-color: #0052FF; border-right: 1px solid #0052FF; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: white !important; }
    .main-header { font-size: 32px; font-weight: 900; color: #0052FF; text-align: center; margin-bottom: 20px; text-transform: uppercase; }
    .card { 
        background: white; border-radius: 12px; padding: 20px; 
        margin-bottom: 15px; border-left: 5px solid #0052FF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .ttn-btn {
        display: inline-block; padding: 8px 16px; background-color: #0052FF;
        color: white !important; border-radius: 6px; text-decoration: none;
        font-weight: bold; font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ ---
S_URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
L_URL = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"

def to_n(v):
    try:
        if isinstance(v, (int, float)): return float(v)
        n = re.findall(r'[-+]?\d*\.?\d+', str(v).replace(' ',''))
        return float(n[0]) if n else 0.0
    except: return 0.0

@st.cache_data(ttl=10)
def load_data():
    try:
        s = pd.read_csv(S_URL).fillna(0)
        l = pd.read_csv(L_URL).fillna("")
        # Чистка мусора
        s = s[~s.iloc[:, 1].astype(str).str.strip().isin(["0", "0.0", "", "СП", "Партнер"])]
        if not l.empty:
            l.iloc[:, 0] = pd.to_datetime(l.iloc[:, 0], errors='coerce')
        return s, l
    except: return pd.DataFrame(), pd.DataFrame()

df_s, df_l = load_data()

# --- 3. ГЛАВНОЕ МЕНЮ (СЛЕВА) ---
with st.sidebar:
    st.markdown("## LIFE PAY")
    st.divider()
    menu = st.radio("РАЗДЕЛЫ:", ["📦 СКЛАД", "📊 ЛОГИСТИКА", "🚚 ОТГРУЗКИ"])
    st.divider()
    st.write("v 2.0 | 2026")

st.markdown(f"<div class='main-header'>LIFE PAY: {menu}</div>", unsafe_allow_html=True)

# --- 4. ЛОГИКА РАЗДЕЛОВ ---

if menu == "📦 СКЛАД":
    st.subheader("Реестр остатков (80 столбцов)")
    search_s = st.text_input("🔍 Поиск по складу (серийник, город):")
    if search_s:
        df_s = df_s[df_s.apply(lambda r: r.astype(str).str.contains(search_s, case=False).any(), axis=1)]
    st.data_editor(df_s, use_container_width=True, height=700, hide_index=True)

elif menu == "📊 ЛОГИСТИКА":
    st.subheader("Сводная аналитика по партнерам")
    # Проверяем наличие нужных столбцов для аналитики
    if df_s.shape[1] >= 12:
        c_map = {
            df_s.columns[1]: "ПАРТНЕР", df_s.columns[3]: "План", df_s.columns[5]: "ККТ",
            df_s.columns[6]: "ФН-15", df_s.columns[7]: "ФН-36", df_s.columns[10]: "Расход 15"
        }
        df_c = df_s.copy()
        for c in list(c_map.keys())[1:]: df_c[c] = df_c[c].apply(to_n)
        summ = df_c.groupby(df_s.columns[1])[list(c_map.keys())[1:]].sum().reset_index()
        summ.rename(columns=c_map, inplace=True)
        st.data_editor(summ, use_container_width=True, hide_index=True)
    else:
        st.warning("В таблице недостаточно столбцов для аналитики.")

elif menu == "🚚 ОТГРУЗКИ":
    if df_l.empty:
        st.error("Данные по отгрузкам не найдены.")
    else:
        # Фильтры
        c1, c2 = st.columns(2)
        with c1:
            cities = sorted([str(x) for x in df_l.iloc[:, 3].unique() if str(x).strip()])
            sel_city = st.selectbox("📍 Выбрать город:", ["Все"] + cities)
        with c2:
            search_l = st.text_input("🔍 Поиск по ТТН / Составу:")
            # Фильтрация
        df_f = df_l.copy()
        if sel_city != "Все": df_f = df_f[df_f.iloc[:, 3].astype(str) == sel_city]
        if search_l: df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(search_l, case=False).any(), axis=1)]

        st.write(f"Найдено: {len(df_f)} отгрузок")
        
        # Вывод карточками
        grid = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with grid[i % 3]:
                # Проверка ссылок (ТТН в 11-м столбце)
                ttn = str(row.iloc[10]) if df_l.shape[1] > 10 else ""
                
                btn_html = f'<a href="{ttn}" target="_blank" class="ttn-btn">🔗 Накладная</a>' if "http" in ttn else f"<b>ТТН:</b> {ttn}"
                
                # Получатель (5 и 6 столбцы)
                rec = f"{row.iloc[4]} | {row.iloc[5]}" if df_l.shape[1] > 5 else "---"

                st.markdown(f"""
                <div class="card">
                    <div style="margin-bottom:10px;">{btn_html}</div>
                    <div style="font-size:15px; font-weight:700; color:#333;">{rec}</div>
                    <div style="margin-top:10px; font-size:12px; color:gray;">
                        📍 {row.iloc[3]} | 📅 {row.iloc[0].strftime('%d.%m.%Y') if pd.notnull(row.iloc[0]) else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📂 Детали и Excel"):
                    st.write(f"Состав: {row.iloc[7] if df_l.shape[1] > 7 else '---'}")
                    csv = pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Скачать Excel", csv, f"row_{i}.csv", "text/csv", key=f"dl_{i}")
