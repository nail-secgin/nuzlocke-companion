import requests
import json
import time
import os
import sys


def resource_path(filename):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, filename)

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)



# Return data from PokéAPI with variable "name" interchangeable for required information
# Resource can be used to access data from the .json like "name"
def return_data(name, resource = None):
    link = "https://pokeapi.co/api/v2/" + name
    response = requests.get(link)

    # If request fails, return None
    if response.status_code != 200:
        return None
    
    data = response.json()
    if resource is not None:
        return data[resource]
    else: 
        return data

# Return Pokémon name for desired language
def pkmn_name(pokemon, language = "en"):
    if pokemon is None:
        return None

    pokemon_species_data = return_data("pokemon-species/" + pokemon)

    if pokemon_species_data is None:
        return None

    name = ""
    for data in pokemon_species_data["names"]:
        if language == data["language"]["name"]:
            name = data["name"]
            
    return name

# 1026 (Number of Pokémon) API requests: Only use for creating your language.json!
def translate_all_pokemon(language):
    if language is None:
        return None

    pokemon_info = []
    for i in range(1, 1030):
        current_pokemon = return_data("pokemon-species/" + str(i))
        if current_pokemon is None:
            break
        for data in current_pokemon["names"]:
            if language == data["language"]["name"]:
                pokemon_info.append({
                    "id" : current_pokemon["id"],
                    "translated_name" : data["name"],
                    "name" : current_pokemon["name"]
                })
        time.sleep(0.15)

    #return pokemon_info

    with open("pokemon_"+str(language)+".json", "w", encoding="utf-8") as file:
        json.dump(pokemon_info, file, indent = 4, ensure_ascii=False)

# Take Pokémon name from any (available) language and return English name
def pkmn_to_eng(pokemon):
    if pokemon is None:
        return None

    languages = ["de"]
    for language in languages:
        file_path = resource_path("pokemon_" + language + ".json")

        with open(file_path, "r", encoding="utf-8") as file:
            pokemon_data = json.load(file)

        for data in pokemon_data:
            # Return English name
            if data["name"].lower() == pokemon.lower():
                return data["name"]
            # Return translated name
            if data["translated_name"].lower() == pokemon.lower():
                return data["name"]
        
    return None

# Return List of Pokémon-varieties
def pkmn_varieties(pokemon):
    if pokemon is None:
        return None
    
    pokemon_species_data = return_data("pokemon-species/" + pokemon)

    if pokemon_species_data is None:
        return None

    pokemon_varieties = []
    for data in pokemon_species_data["varieties"]:
        pokemon_varieties.append(data["pokemon"]["name"])

    return pokemon_varieties

# Return Pokémon Dex-ID
def pkmn_dex_id(pokemon):
    if pokemon is None:
            return None
    
    return return_data("pokemon/" + pokemon, "id")

# Return Pokémon catchrate
def pkmn_catchrate(pokemon, generation, edition):
    if pokemon is None:
            return None

    # Hard-coded because no API data for these specific changes
    # "name" : [catchrate, (before gen)]
    changed_catch_rate = {
        "raticate" : [90, 3],
        "kyogre" : [5, 6],
        "groudon" : [5, 6],
        "rayquaza" : [3, 6],
        "dialga" : [30, 6],
        "palkia" : [30, 6],
        "reshiram" : [45, 6],
        "zekrom" : [45, 6],
        "cosmog" : [45, 9],
        "cosmoem" : [45, 9],
        "solgaleo" : [45, 9],
        "lunala" : [45, 9],
        "poipole" : [3, 8],
        "naganadel" : [3, 8],
        "stakataka" : [3, 8],
        "blacephalon" : [3, 8]
    }

    # Introduced in S/M but catchrate changed in US/UM, needs seperate list because both are from the same generation 
    changed_catch_rate_usum = {
        "buzzwole" : [25, 6],
        "pheromosa" : [255, 6],
        "xurkitree" : [30, 6],
        "celesteela" : [25, 6],
        "kartana" : [255, 6],
        "guzzlord" : [15, 6],
    }

    # Return hard-coded catchrate for Pokémon in dictionaries 
    if pokemon in changed_catch_rate and int(generation) < changed_catch_rate[pokemon][1]:
        return changed_catch_rate[pokemon][0]
        
    if pokemon in changed_catch_rate_usum and (edition == "sun" or edition == "moon"):
        return changed_catch_rate_usum[pokemon][0]


    capture_rate = return_data("pokemon-species/" + pokemon, "capture_rate")

    
    if capture_rate is None:
        # Return catchrate for Pokémon with multiple forms
        pokemon_data = return_data("pokemon/" + pokemon)
        species_name = pokemon_data["species"]["name"]
        return return_data("pokemon-species/" + species_name, "capture_rate")
    else:
        return capture_rate

# Return Pokémon abilities
def pkmn_abilities(pokemon, language="en"):
    if pokemon is None:
            return []
    
    abilities = return_data("pokemon/" + pokemon, "abilities")

    # If Pokémon has no abilities for some reason, return an empty list
    if abilities is None:
        return []
    
    ability_list = []
    for element in abilities:
        ability_list.append(element["ability"]["name"])

    if language != "en":
        for i, ability in enumerate(ability_list):
            pokemon_ability_data = return_data("ability/" + ability)
            for data in pokemon_ability_data["names"]:
                    if language == data["language"]["name"]:
                        ability_list[i] = data["name"]
                        break
    return ability_list

# Return Pokémon moves per intended version group and level
def pkmn_moves(pokemon, version_group, level = 5, language="en"):
    if pokemon is None:
            return []
    
    moves = return_data("pokemon/" + pokemon, "moves")

    if moves is None:
        return []
    
    move_list = []
    level_list = []
    for move in moves:
        for detail in move["version_group_details"]:
            # If the version-group and level match the move, add the moves and levels to the lists
            if detail["version_group"]["name"] == version_group and detail["level_learned_at"] <= level and detail["level_learned_at"] != 0:
                move_list.append(move["move"]["name"])
                level_list.append(detail["level_learned_at"])

    if language != "en":
        for i, move in enumerate(move_list):
            pokemon_move_data = return_data("move/" + move)
            for data in pokemon_move_data["names"]:
                    if language == data["language"]["name"]:
                        move_list[i] = data["name"]
                        break

    # Sort both lists based on the values from level_list
    if move_list:
        move_list, level_list = zip(*sorted(zip(move_list, level_list), key=lambda pair: pair[1]))
    else:
        move_list = []
        level_list = []

    filtered_move = {
        "move_name" : move_list,
        "level" : level_list
    } 

    return filtered_move

# Return Pokémon catch location
def pkmn_home(pokemon):
    if pokemon is None:
            return []
    
    encounters = return_data("pokemon/" + pokemon + "/encounters")

    if encounters is None:
        return None
    
    encounter_list = []
    for element in encounters:
        # Don't forget: Add editions
        encounter_list.append(element["location_area"]["name"])
    return encounter_list

# Return all Pokémon editions and version groups per intended generation
def pkmn_gens(gen):
    name = return_data("generation/" + str(gen), "name")
    version_group = return_data("generation/" + str(gen), "version_groups")

    groups = []
    editions = []
    editions_version_group = []

    # Version-group names in list "groups"
    for group in version_group:
        groups.append(return_data("version-group/" + group["name"]))

    for edition in groups:
        for version in edition["versions"]:
            # List of version groups parallel to list of each edition
            editions_version_group.append(edition["name"])
            editions.append(version["name"])

    gen_data = {
        "name" : name,
        "version_group": version_group,
        "editions" : [editions, editions_version_group]
    }

    return gen_data

# Find pokemon version-group for intended edition
def pkmn_edition_find_versiongroup(edition, generation):
    version_group = ""

    dic = pkmn_gens(generation)

    # Iterate through editions found through pkmn_gens() and return correct version-group 
    for i in range(len(dic["editions"][0])):
            if dic["editions"][0][i] == edition:
                version_group = dic["editions"][1][i]

    return version_group

# Return Pokémon types depending on generation
def pkmn_types(pokemon, gen, language="en"):
    if pokemon is None:
        return []
    
    past_types = return_data("pokemon/" + pokemon, "past_types")
    types = return_data("pokemon/" + pokemon, "types")

    if types is None:
        return []
    
    type_list = []
    if past_types:
        for element in past_types:
            # Get generation number from the last index of the URL
            generation = int(element["generation"]["url"].rstrip("/").split("/")[-1])
            # If the intended generation is smaller than current generation in past_types, use the old types
            if generation >= int(gen):
                for type_data in element["types"]:
                    type_list.append(type_data["type"]["name"])
            # Else if the intended generation is more recent than the last change, use the new types
            else:
                for type_data in types:
                    type_list.append(type_data["type"]["name"])
    else:
        # If no past types exist, use normal types
        for element in types:
            type_list.append(element["type"]["name"])

    if language != "en":
        for i, type in enumerate(type_list):
            type_data = return_data("type/" + type)
            for data in type_data["names"]:
                    if language == data["language"]["name"]:
                        type_list[i] = data["name"]
                        break
    return type_list

# Return Pokémon stats
def pkmn_stats(pokemon, gen):
    if pokemon is None:
            return None

    if gen is None:
            return None
    
    gen = int(gen)

    past_stats = return_data("pokemon/" + pokemon, "past_stats")
    stats = return_data("pokemon/" + pokemon, "stats")

    if stats is None:
        return None, None

    # Generation 1 had one "Special" stat instead of "Special-Attack" and "Special-Defense", so seperate dictionary is useful 
    if gen == 1:
        stats_list = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "special": 0,
            "speed": 0
        }
    else:
        stats_list = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "special-attack": 0,
            "special-defense": 0,
            "speed": 0
        }        

    for stat_data in stats:
        stat = stat_data["stat"]["name"]

        if stat in stats_list and stats_list[stat] is not None:
            stats_list[stat] = stat_data["base_stat"]

    for element in past_stats:
        generation = int(element["generation"]["url"].rstrip("/").split("/")[-1])

        if generation >= gen:
            for stat_data in element["stats"]:
                stat = stat_data["stat"]["name"]

                if stat in stats_list:
                    stats_list[stat] = stat_data["base_stat"]

    # Calculate Total Base Stats
    total_base_stats = sum(stats_list.values())

    return total_base_stats, stats_list

