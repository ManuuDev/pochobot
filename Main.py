import os
import discord
from discord.ext import commands
import configparser
from app.Core import Database
from app.System.ErrorHandler import NoTokenProvided
from app.System.Log import create_main_log, log

################################################## GLOBALS ##################################################


bot = commands.Bot(command_prefix=".", intents=discord.Intents().all())


################################################## GLOBALS ##################################################


def main():

    create_main_log()

    load_cogs()

    Database.init_globals(bot.commands)

    config = loadConfig()
    profile = config['MAIN']['PROFILE']

    if not config.has_option('TOKENS', profile):
        raise NoTokenProvided()

    token = config['TOKENS'][profile]

    bot.run(token)


def load_cogs():
    for filename in os.listdir("app/Cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"app.Cogs.{filename[:-3]}")
            log(f"Cog {filename} cargado")


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


if __name__ == '__main__':
    main()
