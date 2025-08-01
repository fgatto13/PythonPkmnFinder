# api.py
import requests
import tempfile

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

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

def download_cry(data: dict, legacy: bool = False) -> str | None:
    try:
        # Select either the latest or legacy cry URL
        cry_url = data["cries"]["legacy"] if legacy else data["cries"]["latest"]

        # Fetch the audio
        response = requests.get(cry_url)
        response.raise_for_status()

        # Save to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(response.content)
            return tmp.name

    except (KeyError, requests.RequestException) as e:
        print(f"❌ Failed to download cry: {e}")
        return None
