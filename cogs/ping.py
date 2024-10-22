from discord import Interaction, slash_command
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='ping', description='See bot ping', guild_ids=[])
    async def ping(
            self,
            ctx: Interaction
    ):
        await ctx.response.send_message(f'Bot ping {round(self.bot.latency * 1000)} ms !')


def setup(bot):
    bot.add_cog(Ping(bot))
