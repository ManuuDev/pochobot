from discord.ext import commands
from app.messages.poll import start_poll, end_poll
from app.system.utils import get_all_args_as_string, get_timer, send_poll_message, send_response_with_quote_format


class PollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='votacion', aliases=['v'], help='Inicia una votacion')
    async def new_poll(self, ctx, *args):
        poll = await start_poll(ctx, get_all_args_as_string(args))
        poll.current_poll_message = await send_poll_message(ctx, poll)
        function = end_poll(ctx, True)
        poll.timer = get_timer(self.bot, function)
        poll.start_timer()

    @commands.command(name='terminar', aliases=['tv'], help='Termina una votacion')
    async def end_poll(self, ctx, timeout=False):
        await send_response_with_quote_format(ctx, await end_poll(ctx, timeout))


def setup(bot):
    bot.add_cog(PollsCog(bot))
