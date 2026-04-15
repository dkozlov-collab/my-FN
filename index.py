import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Мониторинг Складов", layout="wide", page_icon="📈")

# Ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"

def clean_num(val):
    try:
        return int(float(str(val).replace(',', '.').strip()))
    except:
        return 0

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL).fillna(0)
    for col in ['Остатки ККТ', 'В пути ККТ', 'Мин. остаток']:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)
    return df

# Вход
st.sidebar.title("🔐 Доступ")
pwd = st.sidebar.text_input("Код", type="password")

if pwd == "777":
    try:
        df = load_data()
        st.title("🏗️ Пульт управления складами")

        # СОЗДАЕМ РАЗДЕЛЬНЫЕ ВКЛАДКИ
        t_main, t_partners, t_delivery, t_remote = st.tabs([
            "🏙️ По городам", "🤝 По партнерам", "🚚 Отгрузки / В пути", "🛰️ Удаленка"
        ])

        with t_main:
            st.subheader("Общая динамика по городам")
            # Круглая диаграмма
            fig_pie = px.pie(df, values='Остатки ККТ', names='Склад', title='Доля ККТ на складах')
            st.plotly_chart(fig_pie, use_container_width=True)
            st.bar_chart(df.set_index('Склад')['Остатки ККТ'])

        with t_partners:
            st.subheader("Аналитика по партнерам")
            partner = st.selectbox("Выберите партнера:", df['Сервис Партнер'].unique())
            p_df = df[df['Сервис Партнер'] == partner]
            # Круглая диаграмма для партнера
            fig_p_pie = px.pie(p_df, values='Остатки ККТ', names='Склад', title=f'Склады партнера: {partner}')
            st.plotly_chart(fig_p_pie, use_container_width=True)
            st.dataframe(p_df, use_container_width=True)

        with t_delivery:
            st.subheader("🚚 Мониторинг отгрузок")
            if 'В пути ККТ' in df.columns:
                in_transit = df[df['В пути ККТ'] > 0]
                st.metric("Всего в пути", f"{in_transit['В пути ККТ'].sum()} шт")
                st.dataframe(in_transit[['Склад', 'В пути ККТ', 'Сервис Партнер']], use_container_width=True)
            else:
                st.warning("Колонка 'В пути ККТ' не найдена")

        with t_remote:
            st.subheader("🛰️ Статистика удаленных рег.")
            remote = df[df['Тип рег'].str.contains('Уд', na=False)]
            st.metric("Активных удаленок", len(remote))
            st.dataframe(remote, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка: {e}")
else:
    st.info("Введите пароль для доступа к аналитике")
