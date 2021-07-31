import json
import os
import requests

PREFIX: str = 'databases/'

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

    database_file = open(get_path_with_prefix('responsesDatabase.json'), "r")
    data = json.loads(database_file.read())
    simpleTalkDictionary = data['simpleTalk']
    fastAnswerList = data['genius']['fastAnswer']
    radios = data['radios']


def init_steam_database():
    global indexedGamesDict

    cwd = os.getcwd()
    separator = os.path.sep
    database_path = cwd + separator + PREFIX + 'steamDatabase.json'

    if os.path.isfile(database_path):
        with open(database_path, 'r') as inputfile:
            indexedGamesDict = json.loads(inputfile.read())

    else:
        page = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v0001/")
        json_structure = json.loads(page.content)
        game_list = json_structure['applist']['apps']['app']
        indexedGamesDict = create_abc_for_db(game_list)
        with open(database_path, 'w') as outfile:
            json.dump(indexedGamesDict, outfile)


def create_abc_for_db(game_list):
    dictionary = dict()
    char: str = None

    for item in game_list:
        if item:
            first_char = item.get('name')[0]

            if not char or char != first_char:
                char = first_char
                if char not in dictionary:
                    dictionary[char] = list()

            game_tuple = (item.get('name').strip(), item.get('appid'))
            dictionary[char].append(game_tuple)

    return dictionary


def get_path_with_prefix(filename):
    return PREFIX + filename
