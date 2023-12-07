import nextcord
from nextcord.ext import commands
from nextcord import slash_command


class Ticket(commands.Cog):
    def __init__(self):
        super().__init__(timeout=None)

    @slash_command(name="openticket", description="Open a support ticket.")
    async def open_ticket(self, interaction):
        category_name = "Support Tickets"
        category = nextcord.utils.get(interaction.guild.categories, name=category_name)

        if not category:
            category = await interaction.guild.create_category(category_name)

        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(1069731597861003276): nextcord.PermissionOverwrite(read_messages=True),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)
        }

        channel = await category.create_text_channel(f"ticket-{interaction.author.id}", overwrites=overwrites)
        await channel.send(f"Hello {interaction.author.mention}, please describe your issue.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, nextcord.DMChannel):
            category_name = "Support Tickets"
            category = nextcord.utils.get(message.guild.categories, name=category_name)

            if not category:
                category = await message.guild.create_category(category_name)

            overwrites = {
                message.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                message.author: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
            }

            channel = await category.create_text_channel(f"ticket-{message.author.id}", overwrites=overwrites)
            await channel.send(f"Hello {message.author.mention}, please describe your issue.")


def setup(bot):
    bot.add_cog(Ticket(bot))
