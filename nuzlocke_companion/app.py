from api import *
from pokemon import *
from nuzlocke import *
from storage import *

from flask import Flask, render_template, request, session, redirect, url_for

import os
import secrets
import threading
import webbrowser
from pathlib import Path


app = Flask(__name__)
#app.secret_key = "development-key"

if os.name == "nt":
    DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "PokemonNuzlocke"


DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_FILE = DATA_DIR / "secret.key"

if SECRET_FILE.exists():
    app.secret_key = SECRET_FILE.read_text(encoding="utf-8")
else:
    secret_key = secrets.token_hex(32)
    SECRET_FILE.write_text(secret_key, encoding="utf-8")
    app.secret_key = secret_key

# index.html
@app.route("/")
def home():
    generation = session.get("generation")
    edition_data = session.get("edition")
    return render_template(
                "index.html",
                generation_number = generation,
                edition = edition_data
                )

# nuzlocke.html
@app.route("/nuzlocke", methods=["GET", "POST"])
def nuzlocke():
    # session.get("") returns None if not saved yet, so initialization is successful before first input
    generation = session.get("generation")
    # If generation is not empty, save its data
    # generation is the generation number, generation_data is a list of all editions in the generation
    if generation:
        generation_data = pkmn_gens(generation)["editions"][0]
    else:
        generation_data = []

    edition_data = session.get("edition")
    nuzlocke_name = session.get("nuzlocke_name")

    current_nuzlockes = load_nuzlockes()

    # Get data from html POST
    if request.method == "POST":
        # action is the value from html submit
        action = request.form["action"]

        # If the submit info is for the generation, save the info for the selected generation
        if action == "generation":
            generation = request.form["generation"]
            generation_data = pkmn_gens(generation)["editions"][0]
            session["generation"] = generation
            # If generation is reselected, clear edition selection
            session.pop("edition", None)

        # Save selected edition
        elif action == "edition":
            edition = request.form["edition"]
            edition_data = edition
            session["edition"] = edition

        # Save user input Nuzlocke name
        elif action == "nuzlocke_name":
            nuzlocke_name = request.form["nuzlocke_name"]
            session["nuzlocke_name"] = nuzlocke_name

        # Create Nuzlocke
        elif action == "start":
        # The new Nuzlocke gets the highest ID
            if current_nuzlockes: 
                new_id = current_nuzlockes[-1].id + 1
            # If no Nuzlocke exists, the Nuzlocke gets ID 1
            else:
                new_id = 1
            session["nuzlocke_id"] = new_id
            # Nuzlocke name is optional
            if nuzlocke_name: 
                save_nuzlocke(Nuzlocke(generation, edition_data, id = new_id, name = nuzlocke_name ))
            else:
                save_nuzlocke(Nuzlocke(generation, edition_data, id = new_id, name = None))
            current_nuzlockes = load_nuzlockes()  
            # Redirect to start.html
            return redirect(url_for("start"))

    # Send values to nuzlocke.html / jinja
    return render_template(
        "nuzlocke.html",
        generation = generation_data,
        generation_number = generation,
        edition = edition_data,
        current_nuzlockes = current_nuzlockes,
        nuzlocke_name = nuzlocke_name
        )

# load_nuzlocke.html
@app.route("/load_nuzlocke", methods=["GET", "POST"])
def load_nuzlocke_page():
    current_nuzlockes = load_nuzlockes()
    generation = session.get("generation")
    edition_data = session.get("edition")

    if request.method == "POST":
        action = request.form["action"]
        # Select Nuzlocke by ID and redirect to start.html
        if action == "nuzlocke_button":
            nuzlocke_id = request.form["nuzlocke_id"]
            for nuzlocke in current_nuzlockes:
                if nuzlocke.id == int(nuzlocke_id):
                    # Set sessions when loading Nuzlocke in a new/clean browser
                    session["generation"] = nuzlocke.generation
                    session["edition"] = nuzlocke.edition
                    session["nuzlocke_id"] = int(nuzlocke_id)
                    return redirect(url_for("start"))


    return render_template(
        "load_nuzlocke.html",
        current_nuzlockes = current_nuzlockes,
        generation_number = generation,
        edition = edition_data
        )

# start.html
@app.route("/start", methods=["GET", "POST"])
def start():
    # Get generation and edition data from before
    generation = session.get("generation")
    if generation:
        generation_data = pkmn_gens(generation)["editions"][0]
    else:
        generation_data = []

    edition = session.get("edition")
    # User input Pokémon from search
    found_pokemon =  session.get("found_pkmn")
    # Input level to filter moves
    moves_level = session.get("moves_level")
    nuzlocke_id = session.get("nuzlocke_id")

    abilities = []

    catchrate = None
    types = None
    moves = None
    total_base_stats = None
    dex_id = None
    pokemon_varieties = None
    route = None
    nickname = None
    search_varieties = None
    search_varieties_add = None
    add_varieties = None
    display_name = None
    display_name_search = None

    language = session.get("language", "en")

    # List of all Pokémon for current Nuzlocke
    current_pokemon = load_pokemon(nuzlocke_id)


    if request.method == "POST":
        action = request.form["action"]

        # Search for Pokémon
        if action == "search_pkmn":
            found_pokemon = pkmn_to_eng(request.form["search_pkmn"])
            if found_pokemon is None:
                error = "Pokémon not found"
            else:
                # Check if Pokémon has different forms
                search_varieties_search = pkmn_varieties(found_pokemon)
                # If Pokémon has multiple forms, user has to be able to select them
                if len(search_varieties_search) > 1:
                    search_varieties = search_varieties_search
                    found_pokemon = None
                else:
                    session["found_pkmn"] = found_pokemon
            

        # Select Pokémon form for the search if required
        elif action == "select_form":
            found_pokemon = request.form["pokemon_form"]
            session["found_pkmn"] = found_pokemon
            display_name_search = pkmn_name(found_pokemon, language)

        # Add Pokémon to team
        elif action == "add_pokemon":
            name = pkmn_to_eng(request.form["name"])
            nickname = request.form["nickname"]
            route = request.form["route"]
            search_varieties_add = pkmn_varieties(name)

            # If name is None, no Pokémon was found and nothing happens
            if name is None:
                error = "Pokémon not found"
            # Pokémon has multiple forms...
            elif len(search_varieties_add) > 1:
                add_varieties = search_varieties_add
                session["nickname"] = nickname
                session["route"] = route
            # Add Pokémon               
            else:
                nickname = request.form["nickname"]
                route = request.form["route"]
                # The new Pokémon gets the highest ID
                if current_pokemon: 
                    new_id = current_pokemon[-1].id + 1
                # If Pokémon does not yet exist in the Nuzlocke, the Pokémon gets ID 1
                else:
                    new_id = 1
                save_pokemon(Pokemon(name, nickname, route, True, pkmn_dex_id(name), id = new_id, nuzlocke_id = nuzlocke_id))
                current_pokemon = load_pokemon(nuzlocke_id)

        # Select Pokémon for the Add-Section
        elif action == "select_add_form":
            name = request.form["pokemon_add_form"]
            display_name = name.title()
            nickname = session["nickname"]
            route = session["route"]
            # The new Pokémon gets the highest ID
            if current_pokemon: 
                new_id = current_pokemon[-1].id + 1
            # If ID does not yet exist, the Pokémon has ID 1
            else:
                new_id = 1
            save_pokemon(Pokemon(name, nickname, route, True, pkmn_dex_id(name), id = new_id, nuzlocke_id = nuzlocke_id))
            current_pokemon = load_pokemon(nuzlocke_id)    

        # Filter moves by level
        elif action == "moves_level":
             moves_level = request.form["moves_level"]
             session["moves_level"] = moves_level

        # Delete selected Pokémon
        elif action == "delete_pkmn":
            delete_pokemon(int(request.form["pokemon_id"]))
            current_pokemon = load_pokemon(nuzlocke_id)

        # Switch Pokémon from dead to alive or vice versa
        elif action == "pokemon_state":
            curr_pkmn = load_pokemon(nuzlocke_id)
            for pokemon in curr_pkmn:
                if pokemon.id == int(request.form["pokemon_id"]):
                    pokemon.state = not pokemon.state
                    break
            save_pokemon_list(curr_pkmn)
            current_pokemon = load_pokemon(nuzlocke_id)

        # Change language to German
        elif action == "language_german":
            session["language"] = "de"

        # Change language to English
        elif action == "language_english":
            session["language"] = "en"
            
    language = session.get("language", "en")

    # If user searches for a Pokémon, display multiple values
    if found_pokemon:
        types = pkmn_types(found_pokemon, generation, language)
        total_base_stats = pkmn_stats(found_pokemon, generation)[0]
        dex_id = pkmn_dex_id(found_pokemon)
        catchrate = pkmn_catchrate(found_pokemon, generation, edition)
        abilities = pkmn_abilities(found_pokemon, language)
        version_group = pkmn_edition_find_versiongroup(edition, generation)
        # Only filter moves by level if user inputs one
        if moves_level: 
            moves = pkmn_moves(found_pokemon, version_group, int(moves_level), language)
        else:
            moves = pkmn_moves(found_pokemon, version_group, 5, language)
        found_pokemon = found_pokemon.title()

        # Display name has to be seperate from actual name so storage does not get messed up with different languages
        display_name_search = pkmn_name(found_pokemon, language)
        if display_name_search is None:
            display_name_search = found_pokemon
        else:
            display_name_search = display_name_search.title()

    # Display name has to be seperate from actual name so storage does not get messed up with different languages
    if current_pokemon:
        for pokemon in current_pokemon:
            display_name = pkmn_name(pokemon.name, language)

            if display_name is None:
                pokemon.display_name = pokemon.name.title()
            else:
                pokemon.display_name = display_name

        

    return render_template(
        "start.html",
        generation = generation_data,
        generation_number = generation,
        edition = edition,
        search_pkmn = found_pokemon,
        catchrate = catchrate,
        abilities = abilities,
        moves = moves,
        moves_level = moves_level,
        current_pokemon = current_pokemon,
        types = types,
        total_base_stats = total_base_stats,
        dex_id = dex_id,
        nuzlocke_id = nuzlocke_id,
        pokemon_varieties = pokemon_varieties,
        route = route,
        nickname = nickname,
        search_varieties = search_varieties,
        add_varieties = add_varieties,
        language = language,
        display_name = display_name,
        display_name_search = display_name_search
        )

@app.context_processor
def add_language():
    return {
        "language" : session.get("language", "en")
    }


# Only for testing, comment other one out
if __name__ == "__main__":
   app.run(debug=True)

'''
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    # Open the browser shortly after Flask starts
    threading.Timer(
        1.0,
        lambda: webbrowser.open(f"http://{host}:{port}")
    ).start()

    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False
    )
'''