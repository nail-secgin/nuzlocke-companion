import json
import os
from pathlib import Path

from pokemon import * 
from nuzlocke import *


if os.name == "nt":
    DATA_DIR = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "PokemonNuzlocke"
    )

os.makedirs(DATA_DIR, exist_ok=True)

NUZLOCKE_FILE = os.path.join(DATA_DIR, "nuzlocke.json")
POKEMON_FILE = os.path.join(DATA_DIR, "pokemon.json")

if not os.path.exists(NUZLOCKE_FILE):
    with open(NUZLOCKE_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)

if not os.path.exists(POKEMON_FILE):
    with open(POKEMON_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)
        

def load_nuzlockes():
    #with open("nuzlocke.json", "r") as file:
    with open(NUZLOCKE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    nuzlocke_list = []

    for nuzlocke in data:
        nuzlocke_list.append(Nuzlocke(nuzlocke["generation"], nuzlocke["edition"], nuzlocke["id"], nuzlocke["name"]))

    return nuzlocke_list

def nuzlocke_list_to_dictionary(nuzlocke_list):
    nuzlocke_dictionary_list = []
    
    for nuzlocke in nuzlocke_list:
        nuzlocke_data = {
            "name" : nuzlocke.name,
            "generation" : nuzlocke.generation,
            "edition" : nuzlocke.edition,
            "id" : nuzlocke.id,
        }
        nuzlocke_dictionary_list.append(nuzlocke_data)

    return nuzlocke_dictionary_list

def save_nuzlocke(nuzlocke):
    nuzlocke_list = load_nuzlockes()
    nuzlocke_list.append(nuzlocke)
    
    #with open("nuzlocke.json", "w") as file:
    with open(NUZLOCKE_FILE, "w", encoding="utf-8") as file:
        json.dump(nuzlocke_list_to_dictionary(nuzlocke_list), file)
           
def load_pokemon(nuzlocke_id = None):
    #with open("pokemon.json", "r") as file:
    with open(POKEMON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    pokemon_list = []

    for pokemon in data:
        if nuzlocke_id is not None and pokemon["nuzlocke_id"] != nuzlocke_id:
            continue      
        pokemon_list.append(Pokemon(pokemon["name"], pokemon["nickname"], pokemon["route"], pokemon["state"], pokemon["dex_id"], pokemon["level"], pokemon["location"], pokemon["id"], pokemon["nuzlocke_id"]))

    return pokemon_list

def pokemon_list_to_dictionary(pokemon_list):
    pokemon_dictionary_list = []
    
    for pokemon in pokemon_list:
        pokemon_data = {
            "name" : pokemon.name,
            "nickname" : pokemon.nickname,
            "route" : pokemon.route,
            "state" : pokemon.state,
            "dex_id" : pokemon.dex_id,
            "level" : pokemon.level,
            "location" : pokemon.location,
            "id" : pokemon.id,
            "nuzlocke_id" : pokemon.nuzlocke_id
        }
        pokemon_dictionary_list.append(pokemon_data)

    return pokemon_dictionary_list

def save_pokemon(pokemon):
    pokemon_list = load_pokemon()
    pokemon_list.append(pokemon)

    #with open("pokemon.json", "w") as file:
    with open(POKEMON_FILE, "w", encoding="utf-8") as file:
        json.dump(pokemon_list_to_dictionary(pokemon_list), file)

def save_pokemon_list(pokemon_list):
    #with open("pokemon.json", "w") as file:
    with open(POKEMON_FILE, "w", encoding="utf-8") as file:
            json.dump(pokemon_list_to_dictionary(pokemon_list), file)

def delete_pokemon(id):
    pokemon_list = load_pokemon()

    for pokemon in pokemon_list:
        if pokemon.id == id:
            pokemon_list.remove(pokemon)
            break

    #with open("pokemon.json", "w") as file:
    with open(POKEMON_FILE, "w", encoding="utf-8") as file:
            json.dump(pokemon_list_to_dictionary(pokemon_list), file)

def pokemon_clear():
    #with open("pokemon.json", "w") as file:
    with open(POKEMON_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)

