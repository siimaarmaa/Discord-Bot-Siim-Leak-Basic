from nextcord import ButtonStyle, slash_command
from nextcord.ui import Button, View
from nextcord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='help', description='Siim Leaks Community Bot Commands', guild_ids=[])
    async def help(self, ctx):
        bot_commands = Button(label='Show bot commands', style=ButtonStyle.blurple)

        async def bot_commands_callback(interaction):
            await interaction.response.send_message('/help - Siim Leaks Basic bot command help\n'
                                                    '/joke - Get Random Joke\n'
                                                    '/dog - Get Random Dog picture\n'
                                                    '/ping - Bot ping command\n'
                                                    '/support - Siim Leaks Community Support\n'
                                                    '/unban - Unban user (only for admins)\n'
                                                    '/ai - Ask something in bot\n')

        bot_commands.callback = bot_commands_callback

        myview = View(timeout=180)
        myview.add_item(bot_commands)

        await ctx.send('Siim Leaks Basic bot commands help', view=myview)


def setup(bot):
    bot.add_cog(Help(bot))
