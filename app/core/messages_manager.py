from app.system.constants import ELEMENT, HEADERS, STEAM_COOKIES, HEADERS, STEAM_COOKIES, URLS
from app.system.utils import fetch, split_with_delimiter, add_percentage, generate_string_from_collection, \
    get_similarity_avg_of_phrases
import collections
import random
from types import SimpleNamespace
import aiohttp
import wikipediaapi
from bs4 import BeautifulSoup
from app.core import databases
from app.system.error_handler import EmptyResponse, GameNotFound


class message_with_image:

    def __init__(self, message, embed_image_url):
        self.message: str = message
        self.embed_image_url: str = embed_image_url


def function_switcher(message):
    text = message.content.strip()
    return simple_talk(text)


def wiki_search(text):
    wikipedia = wikipediaapi.Wikipedia(language='es', user_agent="pochobot/1.0 generic-library/0.0")
    wikipedia_page = wikipedia.page(text)

    if wikipedia_page.exists():
        title = wikipedia_page.title
        summary = wikipedia_page.summary[0:1000]

        summary_continuation: str

        if not (summary.endswith('.')):
            summary_continuation = wikipedia_page.summary[1000:2000]
            summary_continuation = summary_continuation.split('.', 1)[0]
            summary = summary + summary_continuation + "."
        return "Te cuento lo que se sobre " + title + ": " + "\n" + summary
    else:
        return "Boludeces no me preguntes"


def genius(text):
    if text.endswith('?'):
        index = random.choice(range(0, len(databases.fastAnswerList)))
        return databases.fastAnswerList[index]
    else:
        return 'Eso no es una pregunta boludo'


def choose(text):
    options = text.split(',')
    if len(options) > 1:
        return random.choice(options).strip()
    else:
        return "No pusiste varias opciones salchichon"


def simple_talk(text):
    return databases.simpleTalkDictionary.get(text)


async def steam_chart(game_name):
    game = steam_search(game_name)
    url_raw = URLS.STEAM_CHARTS.value
    id = game[1]
    url = f'{url_raw}/app/{id}'
    try:

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            response = await fetch(session, url)

            soup = BeautifulSoup(response, 'html.parser')

            div = soup.find(ELEMENT.DIV, id='app-heading')
            image_url: str = ''

            try:
                image_src = div.find_next('img').attrs.get('src')
                image_url = f'{ url_raw + image_src }'
            except:
                pass

            current_playing = div.find_all(ELEMENT.SPAN, class_='num')[0].string

            avg_players = soup.find('td', class_='right num-f italic').string

            text = f'Juego: {game[0]}\nActualmente jugando: {current_playing}\nPromedio mensual: {avg_players}'

            return message_with_image(message=text, embed_image_url=image_url)
    except Exception:
        raise GameNotFound()


def steam_search(game_name):
    first_char = game_name[0]
    list_with_starter_char = databases.indexedGamesDict[first_char.lower()] + databases.indexedGamesDict[first_char.upper()]
    match = max(list_with_starter_char, key=lambda x: get_similarity_avg_of_phrases(x[0], game_name))
    return match


async def search_info_from_steam(game_name):
    appid = steam_search(game_name)[1]
    steam_url = URLS.STEAM_STORE.value + str(appid)

    async with aiohttp.ClientSession(headers=HEADERS, cookies=STEAM_COOKIES) as session:
        response = await fetch(session, steam_url)

    soup = BeautifulSoup(response, 'html.parser')

    Item = collections.namedtuple('Item', 'prefix content')
    items: list = list()

    name = soup.find(ELEMENT.DIV, class_='apphub_AppName')
    if not name:
        raise EmptyResponse('No tengo acceso a la pagina de ese juego')
    items.append(Item(prefix='Nombre: ', content=name))

    div_first_product = soup.find(
        ELEMENT.DIV, 'game_area_purchase_game_wrapper')
    if div_first_product:
        div_price = div_first_product.find(ELEMENT.DIV, class_='game_purchase_action_bg')
    else:
        div_price = soup.find(ELEMENT.DIV, class_='game_purchase_action_bg')

    try:
        price = div_price.find(ELEMENT.DIV, class_='game_purchase_price price')
        discount_price = div_price.find(ELEMENT.DIV, class_='discount_final_price')
        percentage_discount = div_price.find(ELEMENT.DIV, class_='discount_pct')
        if discount_price:
            content = SimpleNamespace(propertyName='string')
            content.string = '({}) {}'.format(percentage_discount.string, discount_price.string)
        else:
            content = price
        items.append(Item(prefix='Precio: ', content=content))
    except AttributeError:
        pass

    percentages = soup.find_all(ELEMENT.DIV, class_='user_reviews_summary_row')

    try:
        recent_reviews = soup.find(ELEMENT.DIV, class_='subtitle column')
        recent_reviews = recent_reviews.find_next_sibling().find(ELEMENT.SPAN)
        if recent_reviews:
            percentage = split_with_delimiter(percentages[0].attrs.get('data-tooltip-html'), '%')
            add_percentage(recent_reviews, percentage)
            items.append(Item(prefix='Reviews recientes: ', content=recent_reviews))
    except AttributeError:
        pass

    try:
        total_reviews = soup.find(ELEMENT.DIV, class_='subtitle column all')
        total_reviews = total_reviews.find_next_sibling().find(ELEMENT.SPAN)
        if total_reviews:
            index = 1 if len(percentages) > 2 else 0
            percentage = split_with_delimiter(percentages[index].attrs.get('data-tooltip-html'), '%')
            add_percentage(total_reviews, percentage)
            items.append(
                Item(prefix='Reviews generales: ', content=total_reviews))
    except AttributeError:
        pass

    try:
        realese_date = soup.find(ELEMENT.DIV, class_='date')
        items.append(
            Item(prefix='Fecha de lanzamiento: ', content=realese_date))
    except AttributeError:
        pass

    try:
        all_languages = soup.find_all('td', class_='ellipsis')
        with_interface_supported = list(filter(lambda x: x.find_next_sibling().find(ELEMENT.SPAN), all_languages))
        if len(with_interface_supported) > 5:
            with_interface_supported = with_interface_supported[:5]
            temp = SimpleNamespace(propertyName='string')
            temp.string = '...'
            with_interface_supported.append(temp)
        with_interface_supported = generate_string_from_collection(with_interface_supported, ', ')
        languages = SimpleNamespace(propertyName='string')
        languages.string = with_interface_supported
        items.append(Item(prefix='Idiomas de interfaz disponibles: ', content=languages))
    except AttributeError:
        pass

    try:
        div = soup.find(ELEMENT.DIV, class_='game_area_sys_req_full')
        if not div:
            div = soup.find(ELEMENT.DIV, class_='game_area_sys_req_leftCol')

        ul = div.find(ELEMENT.UL)
        all_requeriments = ul.find(ELEMENT.UL).find_all(ELEMENT.LI)
        requeriments_string: str = ''

        for requeriment in all_requeriments:
            try:
                element = requeriment.find('strong')
                typo = element.string
                detail = element.next_sibling
                requeriments_string += '{} {}\n'.format(typo, detail)
            except AttributeError:
                pass

        requeriments = SimpleNamespace(propertyName='string')
        requeriments.string = requeriments_string
        items.append(Item(prefix='\nRequisitos minimos:\n', content=requeriments))

    except AttributeError:
        pass

    items = list(filter(lambda x: x and x.content, items))
    message = '\n'.join(map(lambda x: x.prefix + x.content.string.strip(), items))

    is_early_access = soup.find(ELEMENT.DIV, class_='early_access_header')

    if is_early_access:
        message += '\n\n¡El juego esta en early access!, investigalo bien papito'

    return message
