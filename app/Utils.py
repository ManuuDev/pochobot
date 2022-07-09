from discord import Embed
import asyncio
import re
from difflib import SequenceMatcher
from threading import Timer
from youtube_search import YoutubeSearch
from . import Database
from . import ErrorHandler as ErrorHandler


#                               Commands                                  #
def get_all_args_as_string(args):
    return ' '.join(args).strip()


def get_timer(bot, function, seconds=30):
    return Timer(seconds, lambda: asyncio.run_coroutine_threadsafe(function, bot.loop))


#                               Commands                                  #


#                               Responses                                 #
def send_response(ctx, response):
    return ctx.send(response)


def send_response_with_quote(ctx, response):
    return ctx.send('>>> {0}\n{1}'.format(ctx.message.content, response))


def send_response_with_quote_format(ctx, message):
    return ctx.send('```{0}\n```'.format(message))


def send_response_with_specific_quote(ctx, response, quote):
    return ctx.send('>>> {0}\n{1}'.format(quote, response))


async def send_poll_message(ctx, poll):
    message = await send_response_with_quote_format(ctx, poll.response_content)

    for index in range(poll.ammount_of_options):
        await message.add_reaction(Database.numbers[index])

    return message


#                               Responses                                 #


#                             Get ctx values                              #
def get_message_of_context(ctx):
    return ctx.message.content.strip()


def get_channel_from_context(ctx):
    return ctx.message.author.voice.channel


#                             Get ctx values                              #


#                               Multimedia                                #
def get_radio_from_value(url):
    for key, value in Database.radios.items():
        if value == url:
            return key


def similairty_ratio(a, b):
    return SequenceMatcher(None, a, b).quick_ratio()


# En desuso
def get_views(video):
    views = video.get('views')
    if isinstance(views, str):
        views = views.split(' vistas')[0]
        views = views.replace(',', '')
        views = int(views)
    else:
        views = 500000

    return views


def search_for_youtube_video(message=None, search=None):
    search = message.content.strip().replace(
        ' ', '+') if message else search.strip().replace(' ', '+')
    results = YoutubeSearch(search).to_dict()

    if results and len(results) > 0:
        result = results[0]
        suffix = result.get('url_suffix')

        return 'https://www.youtube.com' + suffix
    else:
        raise ErrorHandler.EmptyResponse('No encontre ningun video')


#                               Multimedia                                #


#                                Async IO                                 #

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


#                                Async IO                                 #


#                               Collections                               #
def is_empty(x):
    return not x or len(x) == 0


def strip_strings_from_list(list_of_strings):
    return [x.strip() for x in list_of_strings]


def delete_spaces_from_list(list_of_strings):
    list_of_strings = [x.replace(' ', '') for x in list_of_strings]
    return list_of_strings


def split_with_delimiter(string, delimiter):
    return string.split(delimiter)[0] + delimiter


def get_formatted_query_string(string):
    return re.sub(r'[^A-Za-z0-9\-&%ñÑ+_ ]+', '', string.strip()).lower()


def generate_string_from_collection(collection, concatenator='\n'):
    return concatenator.join(map(lambda x: x.string.strip() if x else ' ', collection))


def add_percentage(item, value):
    item.string += '{}{}{}'.format(' (', value[2:].strip(), ')')


#                               Collections                               #

def get_similarity_avg_of_phrases(a, b):
    a = remove_special_characters(a)
    b = remove_special_characters(b)

    zipped_list = format_as_lists([a, b])

    average = map(lambda x: ratio(x), zipped_list)
    average = sum(average)

    try:
        minus = abs(len(a.split(' ')) - len(b.split(' '))) / 10
    except ZeroDivisionError:
        minus = 0

    return average - minus


def format_as_lists(lists):
    for index, x in enumerate(lists):
        x = x.split(' ')
        try:
            x.remove('')
        except ValueError:
            pass
        try:
            x.remove(' ')
        except ValueError:
            pass
        lists[index] = x

    return list(zip(lists[0], lists[1]))


def ratio(string_tuple):
    return SequenceMatcher(None, string_tuple[0], string_tuple[1]).quick_ratio()


def remove_special_characters(string):
    return re.sub(r'[^A-Za-z0-9ñÑ ]+', ' ', string.strip()).lower()
