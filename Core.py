import logging
from discord.ext import commands
import configparser
from app import Database
from app.ErrorHandler import NoTokenProvided, error_handler
from app.MessagesResponses import function_switcher, wiki_search, genius, choose, \
    steam_chart, search_info_from_steam
from app.Multimedia import (radio, play_from_youtube, play_next_multimedia,
                            disconnect, clean_queue, print_queue, resume, pause)
from app.Poll import startpoll, endpoll
from app.Log import create_main_log, log
from app.Utils import send_response_with_quote, send_poll_message, send_response_with_quote_format, \
    get_all_args_as_string, get_message_of_context, get_timer, send_response


######################### GLOBALS #########################
bot = commands.Bot(command_prefix=".")
######################### GLOBALS #########################


def main():

    Database.init_globals(bot.commands)
    create_main_log()

    config = loadConfig()
    profile = config['MAIN']['PROFILE']

    if not config.has_option('TOKENS', profile):
        raise NoTokenProvided()

    token = config['TOKENS'][profile]

    bot.run(token)


def loadConfig():
    config = configparser.ConfigParser()
    config.read('localconfig/config.cfg')

    if not config.has_section('MAIN'):
        createDefaultConfig(config)

    config.read('localconfig/config.cfg')
    return config


def createDefaultConfig(config):
    config['MAIN'] = {'PROFILE': 'DEV'}

    with open('localconfig/config.cfg', 'w') as configfile:
        config.write(configfile)


def user_is_not_in_blacklist():
    def predicate(ctx):
        return ctx.message.author.id not in Database.blackList

    return commands.check(predicate)


@bot.event
async def on_ready():
    message = 'Logged on as {0}!'.format(bot.user)
    print(message)
    log(message)


@bot.event
async def on_command_error(ctx, exception):
    await error_handler(ctx, exception)


@bot.event
async def on_command(ctx):
    message = f'Comando: {ctx.invoked_with}, Canal: {ctx.channel.name}, Autor: {ctx.author.name}, Argumentos: {ctx.args[1:]} '
    log(message)


@bot.listen()
async def on_message(message):
    if message.author.id in Database.blackList and message.content.startswith(bot.command_prefix):
        await message.channel.send('Estas en la lista negra, no voy a gastar tiempo de CPU en vos')
    else:
        if message.author != bot.user and not message.content.startswith(bot.command_prefix):
            response = function_switcher(message)
            if response:
                await message.channel.send('> {0}\n{1}'.format(message.content, response))


@bot.command(name='wiki', help='El pocho recurre a su gran conocimiento y responde sobre un tema')
@user_is_not_in_blacklist()
async def wiki(ctx, *args):
    await send_response_with_quote(ctx, wiki_search(get_all_args_as_string(args)))


@bot.command(name='info', help='Muestra informacion relevante sobre el juego')
@user_is_not_in_blacklist()
async def steam_game_info(ctx, *args):
    response = await search_info_from_steam(get_all_args_as_string(args))
    await send_response_with_quote_format(ctx, response)


@bot.command(name='jugando', help='El Pocho va a steamchart y te pasa la info de un juego')
@user_is_not_in_blacklist()
async def playing_info(ctx, *args):
    message_img = await steam_chart(get_all_args_as_string(args))
    await send_response(ctx, message_img.embed_image_url)
    await send_response_with_quote_format(ctx, message_img.message)


@bot.command(name='respondeme', help='El pocho puede responder una pregunta que le hagas')
@user_is_not_in_blacklist()
async def answer_question(ctx):
    await send_response_with_quote(ctx, genius(get_message_of_context(ctx)))


@bot.command(name='votacion', aliases=['v'], help='Inicia una votacion')
@user_is_not_in_blacklist()
async def new_poll(ctx, *args):
    poll = await startpoll(ctx, get_all_args_as_string(args))
    poll.current_poll_message = await send_poll_message(ctx, poll)
    function = end_poll(ctx, True)
    poll.timer = get_timer(bot, function)
    poll.start_timer()


@bot.command(name='terminar', aliases=['tv'], help='Termina una votacion')
@user_is_not_in_blacklist()
async def end_poll(ctx, timeout=False):
    await send_response_with_quote_format(ctx, await endpoll(ctx, timeout))


@bot.command(name='elegi', help='El Pocho va a elegir entre las opciones que le des')
@user_is_not_in_blacklist()
async def choose_one(ctx, *args):
    await send_response_with_quote(ctx, choose(get_all_args_as_string(args)))


@bot.command(name='calcular', help='El gran Pocho puede resolver ecuaciones por vos')
@user_is_not_in_blacklist()
async def calculate(ctx, *args):
    result: str
    try:
        result = eval(get_all_args_as_string(args))
    except (ZeroDivisionError, SyntaxError):
        result = '¿Vos queres que te meta un ban?'
    await send_response_with_quote(ctx, result)


@bot.command(name='radio', help='El pocho saca la radio y sintoniza lo que le pidas')
@user_is_not_in_blacklist()
async def play_radio(ctx, genre: str = None):
    await radio(ctx, genre, bot)


@bot.command(name='play', aliases=['p'], help='Reproduce videos de youtube (soporta busquedas)')
@user_is_not_in_blacklist()
async def play_youtube(ctx, *args):
    url = get_all_args_as_string(args)
    await play_from_youtube(ctx, url, bot)


@bot.command(name='skip', aliases=['sk'], help='Reproduce la siguiente cancion')
@user_is_not_in_blacklist()
async def next_song(ctx):
    play_next_multimedia(ctx, bot)


@bot.command(name='resume', help='Reanuda la reproduccion de musica')
@user_is_not_in_blacklist()
async def resume_player(ctx):
    await resume(ctx, bot)


@bot.command(name='pause', help='Pausa la reproduccion de musica')
@user_is_not_in_blacklist()
async def pause_player(ctx):
    await pause(ctx, bot)


@bot.command(name='clean', aliases=['c'], help='Limpia la lista de canciones en cola')
@user_is_not_in_blacklist()
async def clean_multimedia_queue(ctx):
    clean_queue()
    await send_response_with_quote_format(ctx, 'La cola de musica fue reiniciada')


@bot.command(name='queue', aliases=['q'], help='Muestra la lista de canciones en cola')
@user_is_not_in_blacklist()
async def print_multimedia_queue(ctx):
    await print_queue(ctx)


@bot.command(name='stop', aliases=['s'], help='Se va del canal enojado y limpia la lista de musica')
@user_is_not_in_blacklist()
async def disconnect_from_vc(ctx):
    await disconnect(ctx, bot)


if __name__ == '__main__':
    main()
