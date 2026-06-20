from fastapi import FastAPI
from backend.services import get_pokemon_data, get_pokemon_list


app = FastAPI(title="Mini Pokédex Backend")

# смотрим, что бекэнд работает и может отдавать список покемонов и данные по конкретному покемону
@app.get("/health")
def health_check():
    return {"status": "ok"}

# эндпоинт для получения списка покемонов
# используем функцию из services.py, которая обращается к PokeAPI и возвращает список имен покемонов
@app.get("/pokemon-list")
def pokemon_list():
    return get_pokemon_list()

# эндпоинт для получения данных по конкретному покемону
# используем функцию из services.py, она обращается к PokeAPI и возвращает данные по покемону, включая описание, изображение и базовые статы и тд
@app.get("/pokemon/{name}")
def pokemon(name: str):
    return get_pokemon_data(name)