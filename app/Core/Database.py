import json
import requests
from datetime import date, datetime
from app.System.Utils import get_absolute_path as format_path
import os

PREFIX: str = 'databases/'
DATE_FORMAT: str = "%d/%m/%y"
simpleTalkDictionary: dict
indexedGamesDict: dict
radios: dict

fastAnswerList: list
commandsNames: list = list()
numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
blackList = []


def init_globals(commands):
    global commandsNames

    for x in commands:
        commandsNames.append(x.name)

    init_responses_databases()

    init_steam_database()


def init_responses_databases():
    global simpleTalkDictionary, fastAnswerList, radios

    database_file = open(get_database_path("responsesDatabase.json"), "r")
    data = json.loads(database_file.read())
    simpleTalkDictionary = data['simpleTalk']
    fastAnswerList = data['genius']['fastAnswer']
    radios = data['radios']


def init_steam_database():
    global indexedGamesDict

    database_path = get_database_path("steamDatabase.json")

    if os.path.isfile(database_path) and was_created_today(database_path):
        with open(database_path, 'r') as inputfile:
            indexedGamesDict = json.loads(inputfile.read())
    else:
        update_steam_database()


def update_steam_database():
    global indexedGamesDict

    page = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2/")
    json_structure = json.loads(page.content)
    game_list = json_structure['applist']['apps']
    indexedGamesDict = create_steam_index(game_list)

    with open(get_database_path("steamDatabase.json"), 'w') as outfile:
        json.dump(indexedGamesDict, outfile)


def was_created_today(file_path):
    return get_file_creation_date(file_path) == date.today().strftime(DATE_FORMAT)


def get_file_creation_date(path):
    t = os.path.getmtime(path)
    return datetime.fromtimestamp(t).strftime(DATE_FORMAT)


def get_database_path(database_name : str):
    return format_path(f'{PREFIX}{database_name}')


def create_steam_index(game_list):
    dictionary = dict()
    char: str = None

    for game in game_list:
        if game:
            first_char = game.get('name')[0] if len(game.get('name')) > 0 else None

            if not char or char != first_char:
                char = first_char
                if char not in dictionary:
                    dictionary[char] = list()

            game_tuple = (game.get('name').strip(), game.get('appid'))
            dictionary[char].append(game_tuple)

    return dictionary