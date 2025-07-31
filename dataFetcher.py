# api.py
import requests
import tempfile

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
CRY_BASE_URL = "https://play.pokemonshowdown.com/audio/cries"

def get_pokemon_info(name: str) -> dict | None:
    url = f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch Pokémon info: {e}")
        return None

def get_sprite_url(data: dict) -> str | None:
    try:
        return data["sprites"]["front_default"]
    except (KeyError, TypeError):
        return None

def get_types(data: dict) -> list:
    try:
        return [t["type"]["name"] for t in data["types"]]
    except (KeyError, TypeError):
        return []

def download_cry(name: str) -> str | None:
    url = f"{CRY_BASE_URL}/{name.lower()}.mp3"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(response.content)
            return tmp.name
    except requests.RequestException as e:
        print(f"❌ Failed to download cry: {e}")
        return None