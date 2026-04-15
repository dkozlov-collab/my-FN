import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка стиля 2026
st.set_page_config(page_title="RBS: Склад и Логистика", layout="wide", page_icon="🚀")

# Твоя ссылка (проверь доступ "Все, у кого есть ссылка"!)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

@st.cache_data(ttl=15)
def load_all_data():
    try:
        full_df = pd.read_csv(URL).fillna("")
        # Массив Склада (1-80)
        df_stock = full_df.iloc[0:80].copy()
        # Массив Логистики (150+)
        df_logic = full_df.iloc[149:].copy()
        return df_stock, df_logic
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- ВЕРХНЕЕ МЕНЮ ---
st.sidebar.title("💎 RBS HUB 2026")
mode = st.sidebar.radio("Выберите раздел:", ["📊 Остатки ККТ", "🚚 Логистика (150+)"])

df_s, df_l = load_all_data()

# ================= РАЗДЕЛ: СКЛАДЫ =================
if mode == "📊 Остатки ККТ":
    st.markdown("<h1 style='text-align: center;'>🏙️ МОНИТОРИНГ СКЛАДОВ</h1>", unsafe_allow_html=True)
    
    if not df_s.empty:
        # KPI
        c1, c2 = st.columns(2)
        # Чистим числа для графиков
        df_s['Остатки ККТ'] = pd.to_numeric(df_s['Остатки ККТ'].astype(str).str.replace(' ',''), errors='coerce').fillna(0)
        
        c1.metric("📦 ВСЕГО ККТ", f"{int(df_s['Остатки ККТ'].sum())} шт")
        c2.metric("🏙️ ГОРОДОВ", len(df_s[df_s['Остатки ККТ'] > 0]))

        # Модный круг
        fig = px.pie(df_s[df_s['Остатки ККТ'] > 0], values='Остатки ККТ', names='Склад', hole=0.6)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_s, use_container_width=True)

# ================= РАЗДЕЛ: ЛОГИСТИКА =================
else:
    st.markdown("<h1 style='text-align: center; color: #FFA500;'>📦 ОТГРУЗКИ И ПОСЫЛКИ</h1>", unsafe_allow_html=True)
    
    if not df_l.empty:
        search = st.text_input("🔍 Быстрый поиск по логистике (город, трек, комплект)...")
        if search:
            df_l = df_l[df_l.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # РИСУЕМ КВАДРАТИКИ (ПЛИТКИ)
        st.write("### 🚚 Статус отгрузок (Плитки)")
        
        # Берем первые 3 колонки для плитки: Комплект, Куда, Статус/Трек
        items = df_l.values.tolist()
        for i in range(0, len(items), 4):
            cols = st.columns(4)
            for j, item in enumerate(items[i:i+4]):
                with cols[j]:
                    st.markdown(f"""
                    <div style="border: 2px solid #FFA500; border-radius: 10px; padding: 10px; background-color: #1E1E1E; margin-bottom: 10px;">
                        <span style="color: #FFA500; font-weight: bold;">📦 Посылка:</span><br>
                        <span style="font-size: 16px;">{item[0]}</span><br>
                        <small>📍 {item[1] if len(item)>1 else ""}</small><br>
                        <code style="color: #00ffcc;">{item[2] if len(item)>2 else ""}</code>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.write("### 📋 Полный реестр логистики")
        st.dataframe(df_l, use_container_width=True)
    else:
        st.warning("На 150-й строке данных не обнаружено.")
