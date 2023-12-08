from nextcord import slash_command
from nextcord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='help', description='Leaks Community Bot Commands', guild_ids=[])
    async def help(self, ctx):
        await ctx.response.send_message('/help - Siim Leaks Basic bot command help\n'
                                                    '/joke - Get Random Joke\n'
                                                    '/dog - Get Random Dog picture\n'
                                                    '/ping - Bot ping command\n'
                                                    '/support - Leaks Community Support\n'
                                                    '/unban - Unban user (only for admins)\n'
                                                    )


def setup(bot):
    bot.add_cog(Help(bot))
