import requests
from fastapi import HTTPException

# url для доступа к PokeAPI, откуда мы будем получать данные о покемонах
# фиксируем в константе, чтобы не дублировать и легко менять при необходимости
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


# у нас есть три функции: для получения списка имен покемонов, для получения описания покемона и для получения данных по конкретному покемону (описание, изображение и базовые статы и тд)
# описание каждой функции и что она делает - в комментариях к ним ниже


# функция для получения списка имен покемонов для выпадающего списка в интерфейсе
def get_pokemon_list():
    # получаем список всех покемонов (лимит 1000, чтобы точно все поместились)
    url = f"{POKEAPI_BASE_URL}/pokemon?limit=1000"
    response = requests.get(url, timeout=10)

    # если запрос не удался, возвращаем пустой список
    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="Failed to load pokemon list"
        )

    # извлекаем данные из ответа и формируем список имен покемонов
    data = response.json()

    pokemon_names = []
    for pokemon in data["results"]:
        pokemon_names.append(pokemon["name"])

    return pokemon_names


# функция для получения описания покемона
def get_pokemon_description(name: str):
    url = f"{POKEAPI_BASE_URL}/pokemon-species/{name.lower()}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return "No description available."

    data = response.json()

    # PokeAPI возвращает несколько описаний на разных языках, выбираем английское и очищаем от лишних символов
    # flavor_text_entries - это список описаний на разных языках, проходим по нему и ищем английское описание
    for entry in data["flavor_text_entries"]:
        if entry["language"]["name"] == "en":
            # flavor_text может содержать символы переноса строки и другие спецсимволы, которые нужно удалить для корректного отображения
            description = entry["flavor_text"]
            description = description.replace("\n", " ")
            description = description.replace("\f", " ")
            return description

    return "No description available."

# функция для получения данных по конкретному покемону (описание, изображение и базовые статы и тд)
def get_pokemon_data(name: str):
    url = f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}"
    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pokemon not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="Failed to load pokemon data"
        )

    data = response.json()

    # PokeAPI предоставляет несколько вариантов изображений покемона, выбираем официальное, а если его нет, то используем стандартное
    official_image = data["sprites"]["other"]["official-artwork"]["front_default"]
    fallback_image = data["sprites"]["front_default"]

    # формируем словарь с данными по покемону, который будет возвращаться на фронте
    pokemon = {
        "name": data["name"],
        "image": official_image or fallback_image,
        "description": get_pokemon_description(name),
        
        # извлекаем типы, рост, вес, способности и базовые статы покемона из ответа PokeAPI и приводим к удобному формату для отображения
        "types": [
            item["type"]["name"]
            for item in data["types"]
        ],
        # рост и вес в PokeAPI указаны в дециметрах и гектаграммах соответственно, переводим в метры и килограммы для удобства
        "height": data["height"] / 10,
        "weight": data["weight"] / 10,
        "abilities": [
            item["ability"]["name"]
            for item in data["abilities"]
        ],
        "stats": {
            item["stat"]["name"]: item["base_stat"]
            for item in data["stats"]
        }
    }

    return pokemon