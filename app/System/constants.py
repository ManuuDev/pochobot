from enum import Enum


class URLS(Enum):
    YOUTUBE = 'https://www.youtube.com'
    STEAM_STORE = 'https://store.steampowered.com/app/'
    STEAM_CHARTS = 'https://steamcharts.com'
    STEAM_API = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'

class ELEMENT(Enum):
    DIV = 'div'
    LI = 'li'
    UL = 'ul'
    SPAN = 'span'

MAIN_FOLDER_NAME: str = 'pochobot'

HEADERS = {'Accept-Language': 'es-ES, es;q=0.9, en;q=0.5',
           'User-Agent': 'Chrome/80.0'}

STEAM_COOKIES = {
    'wants_mature_content': '1',
    'birthtime': '189302401',
    'lastagecheckage': '1-January-2020',
}
