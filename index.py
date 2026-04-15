import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Настройка страницы в стиле "Топ-Тренды 2026"
st.set_page_config(
    page_title="RBS Warehouse: Cyber-Monitoring 2026",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="collapsed"
)

# 2. Применяем КАСТОМНЫЙ CSS для "Красивого Дизайна" (Темная тема + Неон)
st.markdown("""
<style>
    /* Общий фон страницы - глубокий темный синий */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Стилизация неоновых заголовков */
    h1, h2, h3 {
        color: #00E5FF !important; /* Бирюзовый неон */
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.7);
    }
    
    /* Стилизация карточек-индикаторов */
    .log-card {
        border: 2px solid #00E5FF;
        border-radius: 15px;
        padding: 20px;
        background-color: #161A24;
        margin-bottom: 20px;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }
    
    .log-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.8);
        border-color: #FF00E0; /* Переключается на розовый неон при наведении */
    }

    /* Настройка вида таблиц (DataFrame) */
    .stDataFrame {
        border: 1px solid #444;
        border-radius: 5px;
        background-color: #1A1D24;
    }
</style>
""", unsafe_allow_html=True)

# 3. Твоя рабочая ссылка на таблицу (для Склада)
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

# Функция очистки чисел от мусора
def clean_num(val):
    try:
        s = str(val).replace(' ', '').replace('₽', '').replace(',', '.')
        return int(float(s))
    except: return 0

# Функция поиска колонок, игнорируя регистр и переносы строк
def find_col(df, key):
    for c in df.columns:
        if key.lower() in c.replace('\n', ' ').lower():
            return c
    return None

# Загрузка данных только для Склада (первые 80 строк)
@st.cache_data(ttl=15)
def load_stock_data():
    try:
        df = pd.read_csv(URL).head(80).fillna(0)
        return df
    except Exception as e:
        st.error(f"Ошибка доступа к Google Таблице: {e}")
        return pd.DataFrame()

# ================= ГЛАВНЫЙ ИНТЕРФЕЙС СКЛАДА =================
st.markdown("<h1 style='text-align: center;'>🛰️ RBS GLOBAL: CYBER-WAREHOUSE 2026</h1>", unsafe_allow_html=True)

df = load_stock_data()

if not df.empty:
    # Ищем ключевые колонки в твоей таблице
    c_kkt = find_col(df, 'Остатки ККТ')
    c_sum = find_col(df, 'Сумма')
    c_sp = find_col(df, 'Партнер')
    c_city = find_col(df, 'Склад')

    if c_kkt:
        # Чистим данные
        df[c_kkt] = df[c_kkt].apply(clean_num)
        total_kkt = df[c_kkt].sum()
        
        st.markdown("## 📊 Аналитическая Панель")

        # --- БЛОК 1: НЕОНОВЫЕ СПИДОМЕТРЫ ПРОГРЕССА (Gauge) ---
        col_gauge, col_pie = st.columns([2, 1])
        
        with col_gauge:
            st.write("### Выполнение Плана Наличия")
            # План (задай свою цель здесь, например, 150 шт ККТ на складе)
            plan_goal = 150
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = total_kkt,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Всего ККТ на складах", 'font': {'size': 20, 'color': '#E0E0E0'}},
                delta = {'reference': plan_goal, 'increasing': {'color': "#00ffcc"}},
                gauge = {
                    'axis': {'range': [None, plan_goal], 'tickcolor': "#E0E0E0"},
                    'bar': {'color': "#00E5FF"}, # Бирюзовый
                    'bgcolor': "#262730",
                    'borderwidth': 2,
                    'bordercolor': "#444",
                    'steps': [
                        {'range': [0, plan_goal*0.5], 'color': '#333'},
                        {'range': [plan_goal*0.5, plan_goal*0.8], 'color': '#555'}
                    ],
                    'threshold': {
                        'line': {'color': "#FF00E0", 'width': 4}, # Розовый неон для цели
                        'value': plan_goal*0.9
                    }
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#E0E0E0"})
            st.plotly_chart(fig_gauge, use_container_width=True)

        # --- БЛОК 2: КРУТОЙ "БУБЛИК" С ДОЛЯМИ ПАРТНЕРОВ ---
        with col_pie:
            st.write("### Доли Банков (АБ, ТМ и др.)")
            if c_sp and total_kkt > 0:
                # Трендовый "бублик" с большой дыркой (hole=0.6)
                fig_pie = px.pie(df[df[c_kkt]>0], values=c_kkt, names=c_sp, hole=0.6)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#E0E0E0"}, legend={'font': {'color': '#E0E0E0'}})
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Нет данных для отображения долей.")

        st.divider()

        # --- БЛОК 3: НЕОНОВЫЕ КАРТОЧКИ С СУММАМИ ---
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            # Генерация HTML-карточки
            st.markdown(f"""
            <div class="log-card">
                <h3 style="margin-top:0;">💰 Капитал Склада</h3>
                <h1 style="color: #00E5FF; text-shadow: 0 0 15px #00E5FF;">
                    {df[c_sum].apply(clean_num).sum():,.0f} ₽
                </h1>
                <small style="color: #999;">Общая сумма ККТ на всех складах</small>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
            <div class="log-card">
                <h3 style="margin-top:0;">🏢 Активных складов</h3>
                <h1 style="color: #FF00E0; text-shadow: 0 0 15px #FF00E0;">
                    {len(df[df[c_kkt] > 0])} городов
                </h1>
                <small style="color: #999;">Где есть хотя бы 1 ККТ</small>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

    # --- ТАБЛИЦА (EXCEL ВИД) ---
    st.write("### 📋 Полный реестр остатков (1-80)")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("Проверь доступ в Google Таблице! В ней должна быть нажата кнопка «Поделиться» -> «Все, у кого есть ссылка».")
