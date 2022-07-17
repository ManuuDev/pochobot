from discord.ext import tasks
from app.Log import log

@tasks.loop(minutes=1.0)
async def check_empty_voice_channel(bot):
    if  len(bot.voice_clients) > 0 and len(bot.voice_clients[0].channel.members) == 1:
        await bot.voice_clients[0].disconnect()