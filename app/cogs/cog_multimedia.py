from discord.ext import commands
from app.core.multimedia_manager import clean_queue, disconnect, pause, play_from_youtube, play_next_multimedia, print_queue, radio, resume
from app.system.utils import send_response_with_quote_format, get_all_args_as_string


class MultimediaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='radio', help='El pocho saca la radio y sintoniza lo que le pidas')
    async def play_radio(self, ctx, genre: str = None):
        await radio(ctx, genre, self.bot)

    @commands.command(name='play', aliases=['p'], help='Reproduce videos de youtube (soporta busquedas)')
    async def play_youtube(self, ctx, *args):
        url = get_all_args_as_string(args)
        await play_from_youtube(ctx, url, self.bot)

    @commands.command(name='skip', aliases=['sk'], help='Reproduce la siguiente cancion')
    async def next_song(self, ctx):
        play_next_multimedia(ctx, self.bot)

    @commands.command(name='resume', help='Reanuda la reproduccion de musica')
    async def resume_player(self, ctx):
        await resume(ctx, self.bot)

    @commands.command(name='pause', help='Pausa la reproduccion de musica')
    async def pause_player(self, ctx):
        await pause(ctx, self.bot)

    @commands.command(name='clean', aliases=['c'], help='Limpia la lista de canciones en cola')
    async def clean_multimedia_queue(self, ctx):
        clean_queue()
        await send_response_with_quote_format(ctx, 'La cola de musica fue reiniciada')

    @commands.command(name='queue', aliases=['q'], help='Muestra la lista de canciones en cola')
    async def print_multimedia_queue(self, ctx):
        await print_queue(ctx)

    @commands.command(name='stop', aliases=['s'], help='Se va del canal enojado y limpia la lista de musica')
    async def disconnect_from_vc(self, ctx):
        await disconnect(ctx, self.bot)


def setup(bot):
    bot.add_cog(MultimediaCog(bot))
