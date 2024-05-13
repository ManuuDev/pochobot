from discord.ext import commands

from app.system.utils import send_response_with_quote, send_response_with_quote_format, \
    get_all_args_as_string, get_message_of_context, send_response

from app.messages.messages_responses import function_switcher, wiki_search, genius, choose, \
    steam_chart, search_info_from_steam


class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Bienvenido gordolord {0}.'.format(member.mention))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user and not message.content.startswith(self.bot.command_prefix):
            response = function_switcher(message)
            if response:
                await message.channel.send('> {0}\n{1}'.format(message.content, response))

    @commands.command(name='wiki', help='El pocho recurre a su gran conocimiento y responde sobre un tema')
    async def wiki(self, ctx, *args):
        await send_response_with_quote(ctx, wiki_search(get_all_args_as_string(args)))

    @commands.command(name='info', help='Muestra informacion relevante sobre el juego')
    async def steam_game_info(self, ctx, *args):
        response = await search_info_from_steam(get_all_args_as_string(args))
        await send_response_with_quote_format(ctx, response)

    @commands.command(name='jugando', help='El Pocho va a steamchart y te pasa la info de un juego')
    async def playing_info(self, ctx, *args):
        message_img = await steam_chart(get_all_args_as_string(args))
        await send_response(ctx, message_img.embed_image_url)
        await send_response_with_quote_format(ctx, message_img.message)

    @commands.command(name='respondeme', help='El pocho puede responder una pregunta que le hagas')
    async def answer_question(self, ctx):
        await send_response_with_quote(ctx, genius(get_message_of_context(ctx)))

    @commands.command(name='elegi', help='El Pocho va a elegir entre las opciones que le des')
    async def choose_one(self, ctx, *args):
        await send_response_with_quote(ctx, choose(get_all_args_as_string(args)))

    @commands.command(name='calcular', help='El gran Pocho puede resolver ecuaciones por vos')
    async def calculate(self, ctx, *args):
        result: str
        try:
            result = eval(get_all_args_as_string(args))
        except (ZeroDivisionError, SyntaxError):
            result = '¿Vos queres que te meta un ban?'
        await send_response_with_quote(ctx, result)


def setup(bot):
    bot.add_cog(MessagesCog(bot))
