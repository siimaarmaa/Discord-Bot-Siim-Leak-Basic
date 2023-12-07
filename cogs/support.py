from nextcord import ButtonStyle, slash_command
from nextcord.ui import Button, View
from nextcord.ext import commands


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='support', description='Leaks Community Support', guild_ids=[])
    async def support(self, ctx):
        invite = Button(label="Leaks's Community Offical Invite Link", style=ButtonStyle.blurple)
        homepage = Button(label='Aarmaa IT Services', url='https://aarmaa.ee', style=ButtonStyle.link)

        async def invite_callback(interaction):
            await interaction.response.send_message('https://discord.gg/UmbXvj69Zn')

        invite.callback = invite_callback

        myview = View(timeout=180)
        myview.add_item(invite)
        myview.add_item(homepage)

        await ctx.send("Leaks's Community Support", view=myview)


def setup(bot):
    bot.add_cog(Support(bot))
