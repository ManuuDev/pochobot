import datetime
from discord.ext import commands, tasks
from app.core.databases import update_steam_database
from app.core.finance_manager import get_dollar_quote
from app.system.log import log
from app.system.utils import send_response, send_response_with_quote_format


class TasksCog(commands.Cog):

    channel_id_list_for_dollar_quotes : list = ['995207211297013791']

    def __init__(self, bot):
        self.bot = bot
        self.check_empty_voice_channel_task.start()
        self.update_steam_database_task.start()
        self.dollar_quote_task_opening.start()
        self.dollar_quote_task_close.start()
    
    @tasks.loop(minutes=1.0)
    async def check_empty_voice_channel_task(self):
        if len(self.bot.voice_clients) > 0 and len(self.bot.voice_clients[0].channel.members) == 1:
            await self.bot.voice_clients[0].disconnect()
            log("Desconectado del canal de voz por inactividad")

    @tasks.loop(hours=12.0)
    async def update_steam_database_task(self):
        log("Actualizando base de datos de steam")
        update_steam_database()
        log("Base de datos de steam actualizada")

    @tasks.loop(time=datetime.time(hour=14))
    async def dollar_quote_task_opening(self):
        global channel_id_list_for_dollar_quotes

        message = await get_dollar_quote()
        
        for channel_id in channel_id_list_for_dollar_quotes:
            ctx = await self.bot.fetch_channel(channel_id)
            if message:
                await send_response(ctx, 'Cotizaciones de apertura')
                await send_response_with_quote_format(ctx, message)

    @tasks.loop(time=datetime.time(hour=21))
    async def dollar_quote_task_close(self):
        global channel_id_list_for_dollar_quotes

        message = await get_dollar_quote()

        for channel_id in channel_id_list_for_dollar_quotes:
            ctx = await self.bot.fetch_channel(channel_id)
            if message:
                await send_response(ctx, 'Cotizaciones de cierre')
                await send_response_with_quote_format(ctx, message)


def setup(bot):
    bot.add_cog(TasksCog(bot))
