import re
from app.core import database
from discord.ext import commands
from app.system.log import log
import logging as logging
import traceback as traceback
import app.system.utils as Utils


class CustomUserError(Exception):
    messageToUser: str

    def __init__(self, message_content):
        self.messageToUser = message_content


class CustomSystemError(Exception):
    messageToSystem: str

    def __init__(self, message_content):
        self.messageToSystem = message_content
        log(self.messageToSystem)


class PollError(CustomUserError):
    pass


class MultimediaError(CustomUserError):
    pass


class EmptyResponse(CustomUserError):
    pass


class NoTokenProvided(CustomSystemError):
    def __init__(self):
        super().__init__('Es necesario proveer un token para el perfil seleccionado. Utilice la sección TOKENS en el archivo config.cfg.')


class OutdatedPackages(CustomSystemError):
    def __init__(self, packages: list):
        super().__init__('Parece que algunas dependencias necesarias no estan actualizadas, verifique el archivo de requerimientos. Las dependencias desactualizadas son: {}'.format(packages))


class ErrorChekingOutdatedPackages(CustomSystemError):
    def __init__(self):
        super().__init__('Hubo un error al verificar las versiones de las dependencias.')


class GameNotFound(CustomUserError):
    def __init__(self):
        super().__init__('Fijate de escribir bien el nombre pa.')


async def error_handler(ctx, exception):
    try:
        if hasattr(exception, 'original'):
            raise exception.original
        else:
            raise exception
    except CustomUserError as customUserError:
        await Utils.send_response_with_quote(ctx, customUserError.messageToUser)
    except CustomSystemError as customSystemError:
        log(customSystemError.messageToSystem, level=logging.ERROR)
    except commands.CommandNotFound as exception:
        command_try = re.search('\"(.*)\"', exception.args[0]).group(1)
        if command_try.count('.') == 0:
            match = max(database.commandsNames, key=lambda c: Utils.similairty_ratio(
                c.lower(), command_try.lower()))
            await Utils.send_response_with_quote(ctx, 'Ese comando no existe troesma, el mas parecido es {}'.format(match))
    except commands.CheckFailure:
        pass
    except Exception:
        log(traceback.format_exc(), level=logging.ERROR)
        await Utils.send_response_with_quote(ctx, 'Error al procesar el comando')
