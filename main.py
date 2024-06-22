import json
import os
import re
import subprocess
import sys
import discord
from discord.ext import commands
import configparser
from app.core import database
from app.system.utils import get_absolute_path
from app.system.error_handler import ErrorChekingOutdatedPackages, NoTokenProvided, OutdatedPackages
from app.system.log import create_main_log, log

################################################## GLOBALS ##################################################


bot = commands.Bot(command_prefix=".", intents=discord.Intents().all())


################################################## GLOBALS ##################################################


def main():

    create_main_log()

    check_outdated_packages()

    load_cogs()

    database.init_globals(bot.commands)

    config = load_config()
    profile = config['MAIN']['PROFILE']

    if not config.has_option('TOKENS', profile):
        raise NoTokenProvided()

    token = config['TOKENS'][profile]

    bot.run(token)


def load_cogs():
    for filename in os.listdir(get_absolute_path("app/cogs")):
        if filename.endswith(".py"):
            bot.load_extension(f"app.cogs.{filename[:-3]}")
            log(f"Cog {filename} cargado")


def load_config():
    config = configparser.ConfigParser()
    config.read(get_absolute_path("config/config.cfg"))

    if not config.has_section('MAIN'):
        create_default_config(config)

    config.read(get_absolute_path("config/config.cfg"))
    return config


def create_default_config(config):
    config['MAIN'] = {'PROFILE': 'DEV'}

    with open(get_absolute_path("config/config.cfg", "w")) as configfile:
        config.write(configfile)


def check_outdated_packages():
    try:
        pip_outdated_output = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format', 'json'])
        json_output = [x['name'] for x in json.loads(pip_outdated_output.decode())]

        with open(get_absolute_path("requirements.txt")) as f:
            packages = f.read().split("\n")
            requirements_regex = r'^([^><=]*)$'
            package_names = [re.match(requirements_regex, x) for x in packages]
            outdated_packages = [x.group(0) for x in package_names if x and x in json_output]
            
            if outdated_packages:
                raise OutdatedPackages(outdated_packages)
            
    except OutdatedPackages as exception:
        raise exception
    except Exception as exception:
        raise ErrorChekingOutdatedPackages()


if __name__ == '__main__':
    main()
