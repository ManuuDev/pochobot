from discord.ext import commands

from app.System.ErrorHandler import error_handler
from app.System.Log import log


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        message = 'Logged on as {0}!'.format(self.bot.user)
        print(message)
        log(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await error_handler(ctx, exception)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        message = f'Comando: {ctx.invoked_with}, Canal: {ctx.channel.name}, Autor: {ctx.author.name}, Argumentos: {ctx.args[1:]} '
        log(message)


def setup(bot):
    bot.add_cog(EventsCog(bot))
