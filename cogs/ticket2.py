import nextcord
from nextcord.ext import commands
from nextcord import slash_command
from nextcord.ui import View


class CloseButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(style=nextcord.ButtonStyle.red, label="Close Ticket")

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.message.channel.delete()


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_ticket_channel(self, guild, user):
        category_name = "Support Tickets"
        category = nextcord.utils.get(guild.categories, name=category_name)

        if not category:
            category = await guild.create_category(category_name)

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        channel = await category.create_text_channel(f"ticket-{user.id}", overwrites=overwrites)
        return channel

    @slash_command(name="openticket", description="Open a support ticket.")
    async def open_ticket(self, ctx):
        channel = await self.create_ticket_channel(ctx.guild, ctx.user)

        embed = nextcord.Embed(
            title="Support Ticket",
            description=f"Hello {ctx.user.mention}, please describe your issue.",
            color=nextcord.Color.blue(),
        )

        view = View()
        view.add_item(CloseButton())

        message = await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, nextcord.TextChannel):
            if message.channel.name.startswith("ticket-"):
                view = View()
                view.add_item(CloseButton())
                await message.edit(view=view)


def setup(bot):
    bot.add_cog(Ticket(bot))
