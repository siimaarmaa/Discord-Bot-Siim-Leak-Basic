import nextcord
from nextcord.ext import commands


class Verify(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="To verify", style=nextcord.ButtonStyle.green, custom_id="view_1"
    )
    async def callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        role = interaction.guild.get_role(1123975063419502706)
        logs = interaction.guild.get_channel(1123964791074078720)

        if role in interaction.user.roles:
            await interaction.response.send_message("You are already verified", ephemeral=True)
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message("You have been successfully verified", ephemeral=True)

        await logs.send(f"{interaction.user.mention} was successfully verified")


class VerifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Verify())

    @nextcord.slash_command(description="Verify Setup", default_member_permissions=8)
    async def verify(self, interaction: nextcord.Interaction):
        await interaction.channel.send(view=Verify())
        await interaction.response.send_message("Successful", ephemeral=True)


def setup(bot):
    bot.add_cog(VerifyCog(bot))
