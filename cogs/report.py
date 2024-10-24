import discord
from discord.ext import commands


class USERREPORT(discord.ui.Modal):
    def __init__(self, user):
        super().__init__(
            "Report users",
            timeout=5 * 60,
        )
        self.user = user

        self.reason = discord.ui.TextInput(
            label="Reason",
            min_length=2,
            max_length=1000,
            style=discord.TextInputStyle.paragraph
        )
        self.proofs = discord.ui.TextInput(
            label="Proofs",
            min_length=2,
            max_length=1000,
            style=discord.TextInputStyle.paragraph,
            required=False
        )
        self.add_item(self.reason)
        self.add_item(self.proofs)

    async def callback(self, interaction: discord.Interaction) -> None:
        report_channel = interaction.client.get_channel(1202605650404712478)  # reports
        if self.proofs is None:
            bw = "```/```"

        else:
            bw = f"```{self.proofs.value}```"

        em = discord.Embed(
            title="User reported",
            description=f"User: {self.user.name} ({self.user.id})\nAuthor: {interaction.user.name} "
                        f"({interaction.user.id})"
        )
        em.add_field(name="Reason", value=f"```{self.reason.value}```")
        em.add_field(name="Proofs", value=bw)

        await report_channel.send(embed=em)

        await interaction.response.send_message(f"{self.user.mention} successfully reported", ephemeral=True)


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="Report message")
    async def report(self, interaction: discord.Interaction, message: discord.Message):
        report_channel = self.bot.get_channel(1202605757368115220)  # reports

        em = discord.Embed(
            title="Message reported",
            description=f"```{message.content}```"
        )
        em.add_field(name="Author", value=f"`{message.author.name}`")
        em.add_field(name="User", value=f"`{interaction.user.name}`")

        await report_channel.send(embed=em)
        await interaction.response.send_message(f"Message from {message.author.mention} successfully reported",
                                                ephemeral=True)

    @discord.user_command(name="Report users")
    async def user_report(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_modal(USERREPORT(member))


def setup(bot):
    bot.add_cog(Report(bot))
