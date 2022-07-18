from discord.ext import commands, tasks

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1.0)
    async def check_empty_voice_channel(bot):
        if  len(bot.voice_clients) > 0 and len(bot.voice_clients[0].channel.members) == 1:
            await bot.voice_clients[0].disconnect()


def setup(bot):
    bot.add_cog(TasksCog(bot))