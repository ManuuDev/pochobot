import re
from . import Database
from discord.ext import commands
from .Log import log
import logging as logging
import traceback as traceback
from .Utils import similairty_ratio, send_response_with_quote


class CustomError(Exception):
    messageToUser: str

    def __init__(self, message_content):
        self.messageToUser = message_content


class PollError(CustomError):
    pass


class MultimediaError(CustomError):
    pass


class EmptyResponse(CustomError):
    pass


async def error_handler(ctx, exception):
    try:
        if hasattr(exception, 'original'):
            raise exception.original
        else:
            raise exception
    except CustomError as customError:
        await send_response_with_quote(ctx, customError.messageToUser)
    except commands.CommandNotFound as exception:
        command_try = re.search('\"(.*)\"', exception.args[0]).group(1)
        if command_try.count('.') == 0:
            match = max(Database.commandsNames, key=lambda c: similairty_ratio(
                c.lower(), command_try.lower()))
            await send_response_with_quote(ctx, 'Ese comando no existe troesma, el mas parecido es {}'.format(match))
    except commands.CheckFailure:
        pass
    except Exception:
        log(traceback.format_exc(), level=logging.ERROR)
        await send_response_with_quote(ctx, 'Error al procesar el comando')
