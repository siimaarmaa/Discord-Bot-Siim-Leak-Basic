import nextcord
from nextcord.ext import commands
from nextcord import slash_command


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        channel = await category.create_text_channel(f"ticket-{interaction.user.id}", overwrites=overwrites)
        await channel.send(f"Hello {interaction.user.mention}, please describe your issue.")

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

    @commands.command(name="closeticket", description="Close the support ticket.")
    async def close_ticket(self, interaction):
        # Assuming the ticket channel is named in the format "ticket-{user_id}"
        ticket_channel_name = f"ticket-{interaction.user.id}"
        ticket_channel = nextcord.utils.get(interaction.guild.channels, name=ticket_channel_name)

        if ticket_channel:
            await ticket_channel.delete()
            await interaction.response.send_message(f"Your support ticket has been closed. If you have more questions, feel free to open a new ticket.")
            # You can also send a private message to the user if the ticket is closed
            await interaction.user.send("Your support ticket has been closed. If you have more questions, feel free to open a new ticket.")
        else:
            await interaction.response.send_message("You don't have an open support ticket.")


def setup(bot):
    bot.add_cog(Ticket(bot))
