from discord.ext import commands, tasks
from app.core.database import update_steam_database
from app.system.log import log


class TasksCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1.0)
    async def check_empty_voice_channel_task(bot):
        if len(bot.voice_clients) > 0 and len(bot.voice_clients[0].channel.members) == 1:
            await bot.voice_clients[0].disconnect()
            log("Desconectado del canal de voz por inactividad")

    @tasks.loop(hours=12.0)
    async def update_steam_database_task(bot):
        update_steam_database()
        log("Base de datos de steam actualizada")


def setup(bot):
    bot.add_cog(TasksCog(bot))
