import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# фиксируем URL бэкенда в константе, 
# чтобы не дублировать и легко менять при необходимости
API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Mini Pokédex",
    page_icon="🔥",
    layout="centered"
)


st.title("Мини-покедекс для Семинара Наставника")
st.write(
    "Выберите покемона из списка и просмотрите его базовую информацию, "
    "изображение, описание, базовые характеристики и радарную диаграмму."
    "\n\nК сожалению, из-за ограничений API PokeAPI, все данные представлены на английском языке."
)


# загружаем список имен покемонов при загрузке страницы и кэшируем результат, 
# чтобы не делать лишних запросов к бэкенду при каждом взаимодействии пользователя с интерфейсом
@st.cache_data
def load_pokemon_list():
    response = requests.get(f"{API_URL}/pokemon-list", timeout=10)

    if response.status_code != 200:
        return []

    return response.json()

pokemon_names = load_pokemon_list()

# если не удалось загрузить список покемонов, показываем ошибку и останавливаем выполнение, 
# чтобы не было дальнейших ошибок при попытке отобразить интерфейс
if not pokemon_names:
    st.error("Не удалось загрузить список покемонов. Пожалуйста, убедитесь, что бэкенд запущен и работает корректно.")
    st.stop()

# создаем выпадающий список для выбора покемона, используя загруженный список имен покемонов
selected_pokemon = st.selectbox(
    "Выберите покемона",
    pokemon_names
)


if st.button("Показать информацию"):
    response = requests.get(
        f"{API_URL}/pokemon/{selected_pokemon}",
        timeout=10
    )

    if response.status_code == 200:
        # pokemon - это словарь с данными по покемону, который возвращается бэкендом, 
        # он содержит имя, изображение, описание, типы, рост, вес, способности и базовые статы покемона
        pokemon = response.json()

        # отображаем информацию по покемону: имя, изображение, описание, базовые характеристики и радарную диаграмму
        st.subheader(pokemon["name"].title())

        if pokemon["image"]:
            st.image(pokemon["image"], width=250)

        st.write(pokemon["description"])

        st.markdown("### Общая информация")

        st.write("**Типы:**", ", ".join(pokemon["types"]))
        st.write("**Рост:**", f"{pokemon['height']} m")
        st.write("**Вес:**", f"{pokemon['weight']} kg")
        st.write("**Способности:**", ", ".join(pokemon["abilities"]))

        st.markdown("### Базовые статы")

        # создаем таблицу для базовых статов покемона, используя данные, полученные от бэкенда
        stats_df = pd.DataFrame(
            # items() возвращает пары ключ-значение из словаря pokemon["stats"], 
            # которые мы используем для создания таблицы с колонками "Stat" и "Value"
            pokemon["stats"].items(),
            columns=["Stat", "Value"]
        )

        st.table(stats_df)

        # строим радарную диаграмму для базовых статов покемона, используя plotly, 
        # для этого нам нужно подготовить данные в формате, который требует библиотека:
        
        # список категорий - это названия статов, которые мы берем из ключей словаря pokemon["stats"]
        categories = list(pokemon["stats"].keys())
        # значения - это числовые значения статов
        values = list(pokemon["stats"].values())

        # для радарной диаграммы нужно замкнуть круг, то есть добавить первую категорию и значение в конец списка
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                # r - это радиус, который соответствует значениям статов, 
                # theta - это углы, которые соответствуют категориям статов, 
                # fill="toself" означает, что область под линией будет заполнена цветом, 
                # name - это название серии данных для легенды
                r=values_closed,
                theta=categories_closed,
                fill="toself",
                name=pokemon["name"].title()
            )
        )
        

        # настраиваем внешний вид диаграммы: делаем радиальную ось видимой, задаем диапазон от 0 до 150 (макс стат в PokeAPI),
        # скрываем легенду (она не нужна, так как у нас только одна серия данных), 
        # задаем высоту диаграммы
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 150]
                )
            ),
            showlegend=False,
            height=500
        )

        st.markdown("### Диаграмма-паутинка базовых статов")
        st.plotly_chart(fig, use_container_width=True)

    elif response.status_code == 404:
        st.error("Покемон не найден.")

    else:
        st.error("Что-то пошло не так. Пожалуйста, попробуйте позже.")