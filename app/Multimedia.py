import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Final

import youtube_dl
from discord import VoiceClient, ClientException

from . import Database
from .ErrorHandler import CustomUserError, MultimediaError
from .MultimediaObjects import multimedia_factory
from .Utils import send_response_with_quote, get_channel_from_context, search_for_youtube_video, send_response_with_quote_format, \
    get_radio_from_value, is_empty

# TODO Cache

youtubeQueue: list = list()
lock = Lock()

youtubeRawURl: Final[str] = 'https://www.youtube.com'
youtubePrefixVideoUrl: Final[str] = youtubeRawURl + '/watch?v='


async def radio(ctx, genre, bot):
    url = Database.radios.get(genre)
    try:
        if url:
            await play_audio(ctx, bot, url)
        elif genre and genre != 'apagar':
            await send_response_with_quote(ctx, 'No tengo esa radio incluida')
        else:
            await disconnect(bot, get_channel_from_context(ctx))
    except CustomUserError as exception:
        raise exception


async def play_from_youtube(ctx, url, bot):
    if youtubeRawURl not in url:
        url = search_for_youtube_video(search=url)

    try:
        player = await get_voice_client(ctx, bot)

        if player and player.is_playing():
            await queue_manager(ctx, url, bot)
        else:
            await play_audio(ctx, bot, url=url)

    except CustomUserError as exception:
        raise exception
    except TimeoutError:
        raise MultimediaError(
            'Fijate si tengo permisos para entrar a ese canal')


async def play_audio(ctx, bot, url, multimedia=None):
    player: VoiceClient = await get_voice_client(ctx, bot)

    multimedia = await create_multimedia(ctx, url, bot, multimedia)

    if player.is_playing():
        player.source = multimedia.audioSource
    else:
        player.play(multimedia.audioSource,
                    after=lambda _: play_next_multimedia(ctx, bot))

    response = 'Reproduciendo: {}\nDuracion: {}'.format(
        multimedia.title, multimedia.duration)

    await send_response_with_quote_format(ctx, response)


async def create_multimedia(ctx, url, bot, multimedia=None):
    if youtubeRawURl in url:
        return await get_data_from_youtube(ctx, bot, url, multimedia)
    elif get_radio_from_value(url):
        return multimedia_factory(ctx, url=url, typo='radio')
    else:
        raise MultimediaError('Error al obtener datos del objeto multimedia')


async def get_data_from_youtube(ctx, bot, url, multimedia=None):
    if not multimedia or not multimedia.processed:
        info = get_multimedia_data(url)
        multimedia = multimedia_factory(ctx, url, info)

        if multimedia.typo == 'playlist':
            create_playlist_to_queue_daemon(ctx, info, bot)
            return await get_first_song_of_playlist(ctx, info, bot)

    process_next_songs()

    return multimedia


async def queue_manager(ctx, url, bot):
    info = get_multimedia_metadata(url)
    multimedia = multimedia_factory(ctx, url=url, info=info)

    if multimedia.typo == 'playlist' and multimedia.tracks >= 1:
        create_playlist_to_queue_daemon(ctx, info, bot, full_list=True)
        response = 'Playlist {0} \ncon {1} tracks agregada a la cola'.format(
            multimedia.title, multimedia.tracks)

    elif multimedia.typo == 'playlist':
        first_song_url = get_first_song_url(info)
        first_song_info = get_multimedia_metadata(first_song_url)
        multimedia = multimedia_factory(
            ctx, url=first_song_url, info=first_song_info)
        add_multimedia_to_queue(multimedia)
        response = 'Track agregado a la cola: {0}'.format(multimedia.title)

    else:
        add_multimedia_to_queue(multimedia)
        response = 'Track agregado a la cola: {0}'.format(multimedia.title)

    await send_response_with_quote_format(ctx, response)
    process_next_songs()


def create_playlist_to_queue_daemon(ctx, info, bot, full_list=False):
    queue = info.get('entries')
    if queue and len(queue) > 1:
        index = 0 if full_list else 1
        threading.Thread(target=add_playlist_to_queue, args=(
            ctx, queue[index:], bot), daemon=True).start()


def add_playlist_to_queue(ctx, queue, bot):
    lock.acquire()

    for info in queue:
        url = youtubePrefixVideoUrl + info.get('url')
        multimedia = multimedia_factory(ctx, url=url, typo='song')
        youtubeQueue.append(multimedia)

    lock.release()

    asyncio.run_coroutine_threadsafe(
        send_response_with_quote_format(ctx, '{0} canciones agregadas a la cola'.format(len(queue))), bot.loop)


async def get_first_song_of_playlist(ctx, info, bot):
    first_song_url = get_first_song_url(info)
    return await create_multimedia(ctx, first_song_url, bot)


def get_first_song_url(info):
    entries = info.get('entries')
    if len(entries) > 1:
        first_song = entries[0]
        return youtubePrefixVideoUrl + first_song.get('url')
    else:
        return info.get('webpage_url').split('&list=')[0]


def add_multimedia_to_queue(multimedia):
    lock.acquire()
    youtubeQueue.append(multimedia)
    lock.release()


def play_next_multimedia(ctx, bot):
    global youtubeQueue
    if not is_empty(youtubeQueue):
        multimedia = youtubeQueue.pop(0)
        asyncio.run_coroutine_threadsafe(play_audio(
            multimedia.ctx, bot, multimedia.url, multimedia), bot.loop)
    else:
        asyncio.run_coroutine_threadsafe(send_response_with_quote_format(
            ctx, 'La cola de musica esta vacia'), bot.loop)


async def pause(ctx, bot):
    player: VoiceClient = await get_voice_client(ctx, bot)

    if player.is_playing():
        player.pause()


async def resume(ctx, bot):
    player: VoiceClient = await get_voice_client(ctx, bot)

    if not player.is_playing():
        player.resume()


def delete_from_queue(url, exception):
    for multimedia in youtubeQueue:
        if multimedia.url == url:
            youtubeQueue.remove(multimedia)
        print('Eliminado de la lista: {} \n{}'.format(multimedia.url, exception))


async def print_queue(ctx):
    response: str = ''

    if is_empty(youtubeQueue):
        response = 'La cola de musica esta vacia'
    elif any(not x.processed for x in youtubeQueue[:10]):
        response = 'Procesando audio...'
    else:
        for i, x in enumerate(youtubeQueue[:10], start=1):
            response += '{0}) {1}\n'.format(i, x.title)

    await send_response_with_quote_format(ctx, response)


async def disconnect(ctx, bot):
    player = await get_voice_client(ctx, bot)
    await player.disconnect()
    clean_queue()


def clean_queue():
    lock.acquire()
    youtubeQueue.clear()
    lock.release()


# Utils                                                                   #

def process_next_songs():
    if len(youtubeQueue) > 1:
        executor = ThreadPoolExecutor(10)

        def process(_multimedia):
            info = get_multimedia_data(_multimedia.url)
            _multimedia.fill_fields(info)

        for count, multimedia in enumerate(youtubeQueue):
            if not multimedia.processed:
                executor.submit(process, multimedia)
            if count > 10:
                break


async def get_voice_client(ctx, bot) -> VoiceClient:
    try:
        channel = get_channel_from_context(ctx)
    except AttributeError:
        raise MultimediaError('Tenes que estar conectado a un canal de voz')

    check_permissions(ctx, bot, channel)

    player: VoiceClient = bot.voice_clients[0] if len(
        bot.voice_clients) > 0 else None

    if not player or not player.channel == channel:
        try:
            player = await channel.connect()
        except ClientException:
            raise MultimediaError(
                'Estoy en otro canal troesma, anda y tira un stop')

    return player


def check_permissions(ctx, bot, channel):
    bot_member = ctx.guild.get_member(bot.user.id)
    permissions = channel.permissions_for(bot_member)
    attributes = ['connect', 'speak', 'view_channel']

    if any(not getattr(permissions, y) for y in attributes):
        raise MultimediaError('No tengo los permisos necesarios')


# TODO cookiefile
def get_multimedia_metadata(url):
    options = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
    return extract_info(url, options)


def get_multimedia_data(url):
    options = {
        '--force-ipv4': '0.0.0.0',
        'extract_flat': 'in_playlist',
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'quiet': True,
        'no_warnings': True,
    }

    return extract_info(url, options)


def extract_info(url, options, retry=False):
    with youtube_dl.YoutubeDL(options) as ydl:
        try:
            return ydl.extract_info(url, download=False, extra_info=options)
        except youtube_dl.utils.DownloadError as exception:
            if not retry:
                live_options = {'hls_prefer_native': True}
                return extract_info(url, live_options, retry=True)
            else:
                delete_from_queue(url, exception)
        except Exception as exception:
            delete_from_queue(url, exception)
